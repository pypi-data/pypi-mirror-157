from logging import warning

try:
    from . import ENGHo
    from . import Series
    from . import EPH
    from . import BancoMundial
    from . import YahooFinance
    from . import BymaData
    from . import PresupuestoAbierto
except ImportError:
    import ENGHo
    import Series
    import EPH
    import BancoMundial
    import YahooFinance
    import BymaData
    import PresupuestoAbierto

class INDECError(Exception):
    pass

class WaveError(Exception):
    pass

class TrimesterError(Exception):
    pass

class YearError(Exception):
    pass

class AdvertenciaINDEC(Warning):
    pass

class AdvertenciaRegion(Warning):
    pass

class AuthenticationError(Exception):
    pass


eph = EPH
ENGHO = ENGHo
engho = ENGHo
series = Series
TimeSeries = Series
SeriesDeTiempo = Series
series_de_tiempo = Series
time_series = Series
timeseries = Series
BM = BancoMundial
WB = BancoMundial
WorldBank = BancoMundial
banco_mundial = BancoMundial
world_bank = BancoMundial
yfinance = YahooFinance
yf = YahooFinance
YF = YahooFinance
yahoo_finance = YahooFinance
bd = BymaData
BD = BymaData
bymaData = BymaData
byma_data = BymaData
presupuesto_abierto = PresupuestoAbierto
PA = PresupuestoAbierto
pa = PresupuestoAbierto




        
