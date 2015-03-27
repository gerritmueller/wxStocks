import time, datetime, inspect, config
import wxStocks_db_functions as db
import wxStocks_utilities as utils
def line_number():
	"""Returns the current line number in our program."""
	return "File: %s\nLine %d:" % (inspect.getframeinfo(inspect.currentframe()).filename.split("/")[-1], inspect.currentframe().f_back.f_lineno)

# Suffix key: "_yf" = yahoo finance YHOO, "_ms" = morningstar MORN, "_aa" = AAII stock investor pro, "_nq" = Nasdaq.com data NDAQ

class Stock(object):
	def __init__(self, symbol):
		self.held_list = []
		# held list should take certain values into account
		# account where stock is held
		# number of shares held in that account
		# redundant information seems silly,
		# could keep the shares in the account obj only.

		# Ticker Symbol Key
		#				Class "X"	Preferred	Warrents (currently ignored)
		# wxStocks 		".X" 		".PX" 		Ignored
		#
		# Nasdaq 		"/X"		"^X"		"/WS","/WS/"
		# Morningstar 	".X"		"PRX" 		?
		# Yahoo 		"-X" 		"-PX" 		"-WT"
		# AAII 			".X" 		" PR"		?
		# not yet implimented
		# Bloomberg 	"/X"		"/PX" 		?
		# Google 		?			"-X" 		?

		symbol = symbol.upper()
		if symbol.isalpha():
			self.symbol = symbol
			self.ticker = symbol

			self.nasdaq_symbol = symbol
			self.aaii_symbol = symbol
			self.yahoo_symbol = symbol
			self.morningstar_symbol = symbol

			self.yql_ticker = symbol
		else:
			if "." in symbol:
				if ".P" in symbol:
					# preferred
					self.symbol = symbol
					self.ticker = symbol

					self.nasdaq_symbol = symbol.replace(".P", "^")
					self.yahoo_symbol = symbol.replace(".P", "-P")
					self.morningstar_symbol = symbol.replace(".P", "PR")
					self.aaii_symbol = symbol.replace(".P", " PR")

					self.yql_ticker = symbol.replace(".P", "-P")
				else:
					# CLASS.X shares:
					self.symbol = symbol
					self.ticker = symbol

					self.aaii_symbol = symbol
					self.morningstar_symbol = symbol
					self.nasdaq_symbol = symbol.replace(".", "/")
					self.yahoo_symbol = symbol.replace(".", "-")

					self.yql_ticker = symbol.replace(".", "-")
			if "^" in symbol:
				# Nasdaq preferred
				self.symbol = symbol.replace("^", ".P")
				self.ticker = symbol.replace("^", ".P")

				self.nasdaq_symbol = symbol
				self.yahoo_symbol = symbol.replace("^", "-P")
				self.morningstar_symbol = symbol.replace("^", "PR")
				self.aaii_symbol = symbol.replace("^", " PR")

				self.yql_ticker = symbol.replace("^", "-P")
			if "/" in symbol:
				# Warrants currently ignored but this function should be reexamined if warrents to be included in the future
				# if "/WS" in symbol:
				# 	# Nasdaq Warrent
				# 	if "/WS/" in symbol:
				# 		# more complicated version of the same thing
				# 		self.nasdaq_symbol = symbol
				# 		self.yahoo_symbol = symbol.replace("/WS/","-WT")
				#		# I don't know how morningstar does warrents
				# 	else:
				# 		self.nasdaq_symbol = symbol
				# 		self.yahoo_symbol = symbol.replace("/WS","-WT")
				# 	self.aaii_symbol = None
				
				# If bloomberg is integrated, this will need to be changed for preferred stock
				# if "/P" in symbol:
				# 	pass

				# Nasdaq class share
				self.symbol = symbol.replace("/", ".")
				self.ticker = symbol.replace("/", ".")

				self.nasdaq_symbol = symbol
				self.aaii_symbol = symbol.replace("/", ".")
				self.morningstar_symbol = symbol.replace("/", ".")
				self.yahoo_symbol = symbol.replace("/", ".")

				self.yql_ticker = symbol.replace("/", ".")
			if "-" in symbol:
				if "-P" in symbol:
					# Yahoo preferred
					self.symbol = symbol.replace("-P", ".P")
					self.ticker = symbol.replace("-P", ".P")


					self.yahoo_symbol = symbol
					self.nasdaq_symbol = symbol.replace("-P", "^")
					self.aaii_symbol = symbol.replace("-P", " PR")
					self.morningstar_symbol = symbol.replace("-P", "PR")

					self.yql_ticker = symbol
				else:
					# Yahoo Class
					self.symbol = symbol.replace("-", ".")
					self.ticker = symbol.replace("-", ".")


					self.yahoo_symbol = symbol
					self.nasdaq_symbol = symbol.replace("-", "/")
					self.aaii_symbol = symbol.replace("-", ".")
					self.morningstar_symbol = symbol.replace("-", ".")

					self.yql_ticker = symbol
			if " PR" in symbol:
				# AAII preferred 
				self.symbol = symbol.replace(" PR", ".P")
				self.ticker = symbol.replace(" PR", ".P")


				self.aaii_symbol = symbol
				self.yahoo_symbol = symbol.replace(" PR", "-P")
				self.nasdaq_symbol = symbol.replace(" PR", "^")
				self.morningstar_symbol = symbol.replace(" PR", "PR")
				
				self.yql_ticker = symbol.replace(" PR", "-P")

			# Finally:
			# if morningstar preferred notation "XXXPRX", i don't know how to fix that since "PRE" is a valid ticker

		self.firm_name = ""

		self.epoch = float(time.time())
		self.created_epoch = float(time.time())
		self.updated = datetime.datetime.now()

		self.ticker_relevant = True
		# this will be false if stock falls off major exchanges

		self.last_yql_basic_scrape_update = 0.0
		
		self.last_balance_sheet_update_yf = 0.0
		self.last_balance_sheet_update_ms = 0.0

		self.last_cash_flow_update_yf = 0.0
		self.last_cash_flow_update_ms = 0.0

		self.last_income_statement_update_yf = 0.0
		self.last_income_statement_update_ms = 0.0
		
		self.last_key_ratios_update_ms = 0.0

		self.last_aaii_update_aa = 0.0

		# save new object to db
		#config.GLOBAL_STOCK_DICT[symbol.upper()] = self
		#print type(self)
		#print 'Saving: Stock("%s")' % symbol.upper()
		#db.save_GLOBAL_STOCK_DICT()

	def testing_reset_fields(self):
		self.last_yql_basic_scrape_update = 0.0
		
		self.last_balance_sheet_update_yf = 0.0
		self.last_balance_sheet_update_ms = 0.0

		self.last_cash_flow_update_yf = 0.0
		self.last_cash_flow_update_ms = 0.0

		self.last_income_statement_update_yf = 0.0
		self.last_income_statement_update_ms = 0.0
		
		self.last_key_ratios_update_ms = 0.0

class Account(object): #portfolio
	def __init__(self, id_number, cash = 0, initial_ticker_shares_tuple_list = [], initial_ticker_cost_basis_dict = {}):
		self.id_number = id_number
		self.availble_cash = cash # there is a ticker "CASH" that already exists, ugh
		self.stock_shares_dict = {}
		if initial_ticker_shares_tuple_list:
			for a_tuple in initial_ticker_shares_tuple_list: # ["NAME", int(NumberOfShares)]
				if a_tuple[0] not in self.stock_shares_dict.keys():
					# ticker not already in stock share dict
					self.stock_shares_dict["%s" % a_tuple[0].upper()] = a_tuple[1]
				else:
					# redundant, probably inproperly formatted data
					pass
		self.cost_basis_dict = initial_ticker_cost_basis_dict

	def reset_account(cash = 0, new_stock_shares_tuple_list = [], new_ticker_cost_basis_dict = {}):
		self.availble_cash = cash
		self.stock_shares_dict = {}
		for a_tuple in new_ticker_shares_tuple_list: # ["NAME", int(NumberOfShares)]
			if a_tuple[0].upper() not in self.stock_shares_dict.keys():
				self.stock_shares_dict["%s" % a_tuple[0].upper()] = a_tuple[1]
			else:
				print line_number(), "Error: duplicate stocks in new_stock_shares_tuple_list"
		self.cost_basis_dict = new_ticker_cost_basis_dict

	def update_account(self, updated_cash, updated_stock_shares_tuple_list, updated_ticker_cost_basis_dict = {}):
		self.availble_cash = updated_cash
		for a_tuple in updated_stock_shares_tuple_list: # ["NAME", int(NumberOfShares)]
			if a_tuple[0].upper() not in self.stock_shares_dict.keys():
				self.stock_shares_dict["%s" % a_tuple[0].upper()] = a_tuple[1]
			else: # Redundent, but i'm leaving it in here in case i need to edit this later.
				self.stock_shares_dict["%s" % a_tuple[0].upper()] = a_tuple[1]
		
		if updated_ticker_cost_basis_dict:
			self.update_cost_basises(updated_ticker_cost_basis_dict)

	def update_cost_basises(self, new_ticker_cost_basis_dict):
		for ticker in new_ticker_cost_basis_dict:
			self.cost_basis_dict[ticker.upper()] = new_ticker_cost_basis_dict.get(ticker.upper())

	def add_stock(stock_shares_tuple):
		if stock_shares_tuple[0].upper() not in self.stock_shares_dict.keys():
			self.stock_shares_dict["%s" % a_tuple[0].upper()] = a_tuple[1]
		else: # Redundent, but i'm leaving it in here in case i need to edit this later.
			self.stock_shares_dict["%s" % a_tuple[0].upper()] = a_tuple[1]





