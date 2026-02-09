"""
Nifty 500 Stock List
Complete list of NSE-listed stocks for analysis.
Format: symbol.NS for Yahoo Finance compatibility
"""

# Top 200 most liquid Nifty stocks for faster initial load
# Full Nifty 500 can be enabled by uncommenting the extended list below

NIFTY_STOCKS = [
    # Nifty 50 constituents
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "BHARTIARTL.NS", "SBIN.NS", "KOTAKBANK.NS", "BAJFINANCE.NS",
    "ITC.NS", "LICI.NS", "LT.NS", "HCLTECH.NS", "AXISBANK.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "DMART.NS",
    "ULTRACEMCO.NS", "BAJAJFINSV.NS", "WIPRO.NS", "ONGC.NS", "NTPC.NS",
    "NESTLEIND.NS", "TATAMOTORS.NS", "M&M.NS", "JSWSTEEL.NS", "POWERGRID.NS",
    "TATASTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "TECHM.NS",
    "HINDZINC.NS", "LTIM.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "HDFCLIFE.NS",
    "BRITANNIA.NS", "INDUSINDBK.NS", "GRASIM.NS", "CIPLA.NS", "EICHERMOT.NS",
    "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "BPCL.NS", "HEROMOTOCO.NS",
    
    # Nifty Next 50
    "ADANIGREEN.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "ATGL.NS", "AUROPHARMA.NS",
    "BANDHANBNK.NS", "BANKBARODA.NS", "BERGEPAINT.NS", "BIOCON.NS", "BOSCHLTD.NS",
    "CANBK.NS", "CHOLAFIN.NS", "COLPAL.NS", "DABUR.NS", "DLF.NS",
    "GAIL.NS", "GODREJCP.NS", "HAVELLS.NS", "HINDPETRO.NS", "ICICIPRULI.NS",
    "IDEA.NS", "IDFCFIRSTB.NS", "IGL.NS", "INDHOTEL.NS", "INDIGO.NS",
    "IOC.NS", "IRCTC.NS", "JINDALSTEL.NS", "JSWENERGY.NS", "JUBLFOOD.NS",
    "LALPATHLAB.NS", "LUPIN.NS", "MCDOWELL-N.NS", "MOTHERSON.NS", "MUTHOOTFIN.NS",
    "NAUKRI.NS", "NMDC.NS", "OBEROIRLTY.NS", "OFSS.NS", "PAGEIND.NS",
    "PEL.NS", "PETRONET.NS", "PFC.NS", "PIDILITIND.NS", "PIIND.NS",
    "PNB.NS", "POLYCAB.NS", "RECLTD.NS", "SAIL.NS", "SBICARD.NS",
    "SHREECEM.NS", "SIEMENS.NS", "SRF.NS", "TATACOMM.NS", "TATACONSUM.NS",
    "TATAPOWER.NS", "TORNTPHARM.NS", "TRENT.NS", "UNIONBANK.NS", "UPL.NS",
    "VBL.NS", "VEDL.NS", "VOLTAS.NS", "YESBANK.NS", "ZOMATO.NS",
    
    # Additional large caps for broader coverage
    "ABB.NS", "ACC.NS", "ADANITRANS.NS", "ALKEM.NS", "ASHOKLEY.NS",
    "ASTRAL.NS", "ATUL.NS", "AUBANK.NS", "BALKRISIND.NS", "BEL.NS",
    "BHEL.NS", "BHARATFORG.NS", "CANFINHOME.NS", "CGPOWER.NS", "CONCOR.NS",
    "COROMANDEL.NS", "CROMPTON.NS", "CUMMINSIND.NS", "DEEPAKNTR.NS", "ESCORTS.NS",
    "EXIDEIND.NS", "FEDERALBNK.NS", "GLAND.NS", "GLAXO.NS", "GMRINFRA.NS",
    "GNFC.NS", "GODREJPROP.NS", "GSPL.NS", "GUJGASLTD.NS", "HAL.NS",
    "HDFCAMC.NS", "HONAUT.NS", "IPCALAB.NS", "IRFC.NS", "JKCEMENT.NS",
    "JSL.NS", "KANSAINER.NS", "KEI.NS", "L&TFH.NS", "LICHSGFIN.NS",
    "LTTS.NS", "MANAPPURAM.NS", "MFSL.NS", "MGL.NS", "MINDTREE.NS",
    "MPHASIS.NS", "MRF.NS", "NAM-INDIA.NS", "NATIONALUM.NS", "NAVINFLUOR.NS",
    "NIACL.NS", "OIL.NS", "PAYTM.NS", "PERSISTENT.NS", "PFIZER.NS",
    "PHOENIXLTD.NS", "PRESTIGE.NS", "PVRINOX.NS", "RAMCOCEM.NS", "RBLBANK.NS",
    "RELAXO.NS", "SCHAEFFLER.NS", "SHRIRAMFIN.NS", "SONACOMS.NS", "STAR.NS",
    "SUNDARMFIN.NS", "SUNTV.NS", "SYNGENE.NS", "TATACHEM.NS", "TATAELXSI.NS",
    "TIINDIA.NS", "TIMKEN.NS", "TVSMOTOR.NS", "UBL.NS", "UCOBANK.NS",
    "INDIAMART.NS", "IIFL.NS", "IREDA.NS", "KALYANKJIL.NS", "KAYNES.NS",
    "KPITTECH.NS", "LAURUSLABS.NS", "MARICO.NS", "MAXHEALTH.NS", "MCX.NS",
    "METROPOLIS.NS", "NHPC.NS", "NYKAA.NS", "PATANJALI.NS", "POLICYBZR.NS",
    "PW.NS", "RAJESHEXPO.NS", "SOLARINDS.NS", "SONATSOFTW.NS", "SUPREMEIND.NS",
    "SUVENPHAR.NS", "SUZLON.NS", "THERMAX.NS", "TRITURBINE.NS", "TTML.NS",
    
    # ========== SMALL CAP STOCKS ==========
    # High growth potential small caps
    "AARTIIND.NS", "AFFLE.NS", "APLAPOLLO.NS", "ARE&M.NS", "AVANTIFEED.NS",
    "BDL.NS", "BEML.NS", "BLUESTARCO.NS", "BRIGADE.NS", "BSE.NS",
    "CAMPUS.NS", "CARTRADE.NS", "CDSL.NS", "CENTRALBK.NS", "CESC.NS",
    "CLEAN.NS", "COCHINSHIP.NS", "CRISIL.NS", "CYIENT.NS", "DATAPATTNS.NS",
    "DCMSHRIRAM.NS", "DELHIVERY.NS", "DEVYANI.NS", "DIXON.NS", "EASEMYTRIP.NS",
    "ECLERX.NS", "EIDPARRY.NS", "ELGIEQUIP.NS", "EMAMILTD.NS", "ENGINERSIN.NS",
    "EQUITASBNK.NS", "FINCABLES.NS", "FINEORG.NS", "FLUOROCHEM.NS", "FSL.NS",
    "GALAXYSURF.NS", "GARFIBRES.NS", "GESHIP.NS", "GRINDWELL.NS", "GRSE.NS",
    "GSFC.NS", "HAPPSTMNDS.NS", "HATSUN.NS", "HFCL.NS", "HINDCOPPER.NS",
    "HOMEFIRST.NS", "HUDCO.NS", "IIFLWAM.NS", "INDIGOPNTS.NS", "INTELLECT.NS",
    "IOB.NS", "JBCHEPHARM.NS", "JBMA.NS", "JINDALSAW.NS", "JKLAKSHMI.NS",
    "JKPAPER.NS", "JMFINANCIL.NS", "JSWINFRA.NS", "JTEKTINDIA.NS", "JUBLINGREA.NS",
    "KAJARIACER.NS", "KEC.NS", "KRBL.NS", "LATENTVIEW.NS", "LAXMIMACH.NS",
    "LEMONTREE.NS", "LLOYDSME.NS", "LTF.NS", "MAHABANK.NS", "MAHLIFE.NS",
    "MAHSEAMLES.NS", "MAPMYINDIA.NS", "MASTEK.NS", "MAZAGON.NS", "MEDANTA.NS",
    "MEDPLUS.NS", "MIDHANI.NS", "MINDACORP.NS", "MMTC.NS", "MOIL.NS",
    "NATCOPHARM.NS", "NBCC.NS", "NCC.NS", "NETWORK18.NS", "NIITMTS.NS",
    "OLECTRA.NS", "ORIENTELEC.NS", "PNBHOUSING.NS", "PNCINFRA.NS", "PRSMJOHNSN.NS",
    "QUICKHEAL.NS", "RADICO.NS", "RAIN.NS", "RALLIS.NS", "RATNAMANI.NS",
    "RAYMOND.NS", "RCF.NS", "REDINGTON.NS", "RENUKA.NS", "RITES.NS",
    "RMDR.NS", "ROUTE.NS", "RVNL.NS", "SAPPHIRE.NS", "SARDAEN.NS",
    "SHARDACROP.NS", "SHYAMMETL.NS", "SKFINDIA.NS", "SNOWMAN.NS", "SOBHA.NS",
    "SPARC.NS", "SPLPETRO.NS", "STARHEALTH.NS", "STLTECH.NS", "SUNDRMFAST.NS",
    "TANLA.NS", "TATAINVEST.NS", "TCI.NS", "TECHNO.NS", "THYROCARE.NS",
    "TINPLATE.NS", "TRIDENT.NS", "UJJIVAN.NS", "UTIAMC.NS", "VAIBHAVGBL.NS",
    "VAKRANGEE.NS", "VENKEYS.NS", "VGUARD.NS", "VIJAYA.NS", "VIPIND.NS",
    "VSTIND.NS", "WABCOINDIA.NS", "WELCORP.NS", "WELSPUNLIV.NS", "WESTLIFE.NS",
    "WHIRLPOOL.NS", "ZEEL.NS", "ZENSARTECH.NS", "ZFCVINDIA.NS", "ZODIACJRD.NS",
]

# Stock sector mapping for sector analysis
STOCK_SECTORS = {
    # Banking & Finance
    "HDFCBANK.NS": "Banking", "ICICIBANK.NS": "Banking", "SBIN.NS": "Banking",
    "KOTAKBANK.NS": "Banking", "AXISBANK.NS": "Banking", "INDUSINDBK.NS": "Banking",
    "BAJFINANCE.NS": "NBFC", "BAJAJFINSV.NS": "NBFC", "SBILIFE.NS": "Insurance",
    "HDFCLIFE.NS": "Insurance", "ICICIPRULI.NS": "Insurance", "SBICARD.NS": "NBFC",
    "MUTHOOTFIN.NS": "NBFC", "CHOLAFIN.NS": "NBFC", "BANDHANBNK.NS": "Banking",
    "IDFCFIRSTB.NS": "Banking", "PNB.NS": "Banking", "BANKBARODA.NS": "Banking",
    "CANBK.NS": "Banking", "FEDERALBNK.NS": "Banking", "YESBANK.NS": "Banking",
    "AUBANK.NS": "Banking", "RBLBANK.NS": "Banking", "PFC.NS": "NBFC",
    "RECLTD.NS": "NBFC", "LICHSGFIN.NS": "NBFC", "CANFINHOME.NS": "NBFC",
    "HDFCAMC.NS": "AMC", "NAM-INDIA.NS": "AMC",
    
    # IT & Technology
    "TCS.NS": "IT", "INFY.NS": "IT", "HCLTECH.NS": "IT", "WIPRO.NS": "IT",
    "TECHM.NS": "IT", "LTIM.NS": "IT", "MPHASIS.NS": "IT", "COFORGE.NS": "IT",
    "PERSISTENT.NS": "IT", "LTTS.NS": "IT", "TATAELXSI.NS": "IT",
    "NAUKRI.NS": "IT", "KPITTECH.NS": "IT",
    
    # Oil & Gas
    "RELIANCE.NS": "Oil & Gas", "ONGC.NS": "Oil & Gas", "BPCL.NS": "Oil & Gas",
    "IOC.NS": "Oil & Gas", "HINDPETRO.NS": "Oil & Gas", "GAIL.NS": "Oil & Gas",
    "OIL.NS": "Oil & Gas", "PETRONET.NS": "Oil & Gas", "IGL.NS": "Oil & Gas",
    "MGL.NS": "Oil & Gas", "GSPL.NS": "Oil & Gas", "GUJGASLTD.NS": "Oil & Gas",
    "ATGL.NS": "Oil & Gas",
    
    # Pharma & Healthcare
    "SUNPHARMA.NS": "Pharma", "DRREDDY.NS": "Pharma", "CIPLA.NS": "Pharma",
    "DIVISLAB.NS": "Pharma", "APOLLOHOSP.NS": "Healthcare", "LUPIN.NS": "Pharma",
    "AUROPHARMA.NS": "Pharma", "BIOCON.NS": "Pharma", "TORNTPHARM.NS": "Pharma",
    "ALKEM.NS": "Pharma", "IPCALAB.NS": "Pharma", "GLAND.NS": "Pharma",
    "LALPATHLAB.NS": "Healthcare", "MAXHEALTH.NS": "Healthcare",
    "METROPOLIS.NS": "Healthcare", "SYNGENE.NS": "Pharma",
    
    # Auto & Auto Ancillary
    "TATAMOTORS.NS": "Auto", "M&M.NS": "Auto", "MARUTI.NS": "Auto",
    "BAJAJ-AUTO.NS": "Auto", "HEROMOTOCO.NS": "Auto", "EICHERMOT.NS": "Auto",
    "TVSMOTOR.NS": "Auto", "ASHOKLEY.NS": "Auto", "MOTHERSON.NS": "Auto Ancillary",
    "BOSCHLTD.NS": "Auto Ancillary", "BHARATFORG.NS": "Auto Ancillary",
    "BALKRISIND.NS": "Auto Ancillary", "MRF.NS": "Auto Ancillary",
    "EXIDEIND.NS": "Auto Ancillary", "TIINDIA.NS": "Auto Ancillary",
    
    # Metals & Mining
    "TATASTEEL.NS": "Metals", "JSWSTEEL.NS": "Metals", "HINDZINC.NS": "Metals",
    "VEDL.NS": "Metals", "COALINDIA.NS": "Mining", "NMDC.NS": "Mining",
    "JINDALSTEL.NS": "Metals", "SAIL.NS": "Metals", "NATIONALUM.NS": "Metals",
    "JSL.NS": "Metals",
    
    # Infrastructure & Construction
    "LT.NS": "Infrastructure", "ADANIPORTS.NS": "Infrastructure",
    "ULTRACEMCO.NS": "Cement", "SHREECEM.NS": "Cement", "AMBUJACEM.NS": "Cement",
    "ACC.NS": "Cement", "GRASIM.NS": "Cement", "JKCEMENT.NS": "Cement",
    "RAMCOCEM.NS": "Cement", "DLF.NS": "Real Estate", "GODREJPROP.NS": "Real Estate",
    "OBEROIRLTY.NS": "Real Estate", "PRESTIGE.NS": "Real Estate",
    "PHOENIXLTD.NS": "Real Estate",
    
    # Power & Utilities
    "NTPC.NS": "Power", "POWERGRID.NS": "Power", "TATAPOWER.NS": "Power",
    "ADANIGREEN.NS": "Power", "ADANIPOWER.NS": "Power", "JSWENERGY.NS": "Power",
    "NHPC.NS": "Power", "IRFC.NS": "Infrastructure",
    
    # FMCG & Consumer
    "HINDUNILVR.NS": "FMCG", "ITC.NS": "FMCG", "NESTLEIND.NS": "FMCG",
    "BRITANNIA.NS": "FMCG", "TATACONSUM.NS": "FMCG", "DABUR.NS": "FMCG",
    "MARICO.NS": "FMCG", "GODREJCP.NS": "FMCG", "COLPAL.NS": "FMCG",
    "VBL.NS": "FMCG", "UBL.NS": "FMCG", "MCDOWELL-N.NS": "FMCG",
    "JUBLFOOD.NS": "Food & Beverages", "ZOMATO.NS": "Food Tech",
    "PATANJALI.NS": "FMCG",
    
    # Retail & Consumer Durables
    "TITAN.NS": "Retail", "DMART.NS": "Retail", "TRENT.NS": "Retail",
    "PAGEIND.NS": "Retail", "RELAXO.NS": "Retail", "KALYANKJIL.NS": "Retail",
    "NYKAA.NS": "Retail", "VOLTAS.NS": "Consumer Durables",
    "HAVELLS.NS": "Consumer Durables", "CROMPTON.NS": "Consumer Durables",
    "POLYCAB.NS": "Consumer Durables", "KEI.NS": "Consumer Durables",
    
    # Paints & Chemicals
    "ASIANPAINT.NS": "Paints", "BERGEPAINT.NS": "Paints", "KANSAINER.NS": "Paints",
    "PIDILITIND.NS": "Chemicals", "SRF.NS": "Chemicals", "PIIND.NS": "Chemicals",
    "ATUL.NS": "Chemicals", "DEEPAKNTR.NS": "Chemicals", "NAVINFLUOR.NS": "Chemicals",
    "TATACHEM.NS": "Chemicals", "GNFC.NS": "Chemicals", "COROMANDEL.NS": "Chemicals",
    
    # Telecom & Media
    "BHARTIARTL.NS": "Telecom", "IDEA.NS": "Telecom", "TATACOMM.NS": "Telecom",
    "INDIGO.NS": "Aviation", "IRCTC.NS": "Travel", "INDHOTEL.NS": "Hotels",
    "PVRINOX.NS": "Media", "SUNTV.NS": "Media", "STAR.NS": "Media",

    # Conglomerates & Others
    "ADANIENT.NS": "Conglomerate", "SIEMENS.NS": "Engineering",
    "ABB.NS": "Engineering", "HONAUT.NS": "Engineering", "HAL.NS": "Defence",
    "BEL.NS": "Defence", "BHEL.NS": "Engineering", "CUMMINSIND.NS": "Engineering",
    "THERMAX.NS": "Engineering", "CGPOWER.NS": "Engineering",
    "ESCORTS.NS": "Engineering", "ASTRAL.NS": "Plastics",
    "SUPREMEIND.NS": "Plastics", "LICI.NS": "Insurance",
}


def get_stock_sector(symbol: str) -> str:
    """Get sector for a stock symbol."""
    return STOCK_SECTORS.get(symbol, "Others")


def get_stocks_by_sector(sector: str) -> list:
    """Get all stocks in a particular sector."""
    return [s for s, sec in STOCK_SECTORS.items() if sec == sector]


def get_all_sectors() -> list:
    """Get list of unique sectors."""
    return list(set(STOCK_SECTORS.values()))


# Nifty 50 index symbol
NIFTY_INDEX = "^NSEI"
