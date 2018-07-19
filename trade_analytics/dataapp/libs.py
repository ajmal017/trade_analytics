from __future__ import division
import pandas as pd
import stockapp.models as stkmd
from django.db import connections
from dataapp import models as dtamd
import datetime
from talib import abstract
import logging

logger = logging.getLogger('dataapp')


import pdb


def get_trading_dates():
    return dtamd.TradingDates.objects.all().values_list('Date',
                                                        flat=True).distinct()


def StockDataFrame_sanitize(df, standardize=False):
    if len(df) == 0:
        return df

    df['Close'] = df['Close'].astype(float)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Volume'] = df['Volume'].astype(int)

    def setdate(x):
        if isinstance(x, basestring):
            return pd.to_datetime(x).date()
        if isinstance(x, datetime.datetime) or isinstance(
                x, pd.datetime) or isinstance(x, pd.Timestamp):
            return x.date()

        return x

    if 'Date' in df.columns:
        df['Date'] = df['Date'].apply(setdate)
        df.sort_values(by=['Date'], inplace=True)

    # pdb.set_trace()

    index_is_datetype = False
    if isinstance(df.index[0], basestring):
        try:
            pd.to_datetime(df.index[0]).date()
            index_is_datetype = True
        except:
            index_is_datetype = False
    elif isinstance(df.index[0], datetime.datetime) \
            or isinstance(df.index[0], pd.datetime) \
            or isinstance(df.index[0], datetime.date) \
            or isinstance(df.index[0], pd.Timestamp):

        index_is_datetype = True

    if index_is_datetype:
        df.index = map(lambda x: setdate(x), df.index)

    if standardize:
        df.index = df['Date']
        df.drop(['Date'], axis=1, inplace=True)
        if 'id' in df.columns:
            df.drop(['id'], axis=1, inplace=True)
        if 'Symbol_id' in df.columns:
            df.drop(['Symbol_id'], axis=1, inplace=True)
        df.sort_index(inplace=True)

    return df


def addindicators(df, cols):
    if len(cols) == 0:
        return df

    inputs = {
        'open': df['Open'].values,
        'high': df['High'].values,
        'low': df['Low'].values,
        'close': df['Close'].values,
        'volume': df['Volume'].values
    }
    for cc in cols:
        if cc['colname'] not in df.columns:
            try:
                if cc['name'] == 'CCI':
                    df[cc['colname']] = abstract.CCI(
                        inputs, timeperiod=cc['timeperiod'])
                    df[cc['colname']] = df[cc['colname']].astype(float)

                elif cc['name'] == 'SMA':
                    df[cc['colname']] = df['Close'].rolling(
                        window=cc['timeperiod']).mean()
                    df[cc['colname']] = df[cc['colname']].astype(float)

                elif cc['name'] == 'SMAstd':
                    df[cc['colname']] = df['Close'].rolling(
                        window=cc['timeperiod']).std()

                elif cc['name'] == 'EMA':
                    df[cc['colname']] = df['Close'].ewm(
                        span=cc['timeperiod']).mean()
                    df[cc['colname']] = df[cc['colname']].astype(float)

                elif cc['name'] == 'EMAstd':
                    df[cc['colname']] = df['Close'].ewm(
                        span=cc['timeperiod']).std(bias=False)
                    df[cc['colname']] = df[cc['colname']].astype(float)
                elif cc['name'] == 'VolSMA':
                    df[cc['colname']] = df['Volume'].rolling(
                        window=cc['timeperiod']).mean()
                    df[cc['colname']] = df[cc['colname']].astype(float)
                else:
                    print "Indicator not available"

            except Exception as e:
                print "error adding indicator ", cc['colname']
                logger.error("error adding indicator " +
                             cc['colname'] + " " + str(type(e)) + " " + str(e))
                logger.exception(e)

    return df


def GetStockData(Symbolids, Fromdate=pd.datetime(2002, 1, 1).date(),
                 Todate=pd.datetime.today().date(), format='concat',
                 standardize=True, addcols=None):
    if isinstance(Symbolids, list):
        Symbolids = list(Symbolids)

    elif isinstance(Symbolids, tuple):
        Symbolids = list(Symbolids)

    elif isinstance(Symbolids, int) or \
            isinstance(Symbolids, basestring) is True:
        Symbolids = list([Symbolids])

    if isinstance(Symbolids[0], basestring) is True:
        for i in range(len(Symbolids)):
            Symbolids[i] = stkmd.Stockmeta.objects.get(
                Symbol=Symbolids[i]).id

    Symbolids = tuple(Symbolids)
    if len(Symbolids) == 1:

        sqlquery = "SELECT * FROM dataapp_stockprice as dsp \
        WHERE dsp.\"Symbol_id\" = %(ids)s AND dsp.\"Date\" \
        BETWEEN '%(fromdate)s' AND '%(todate)s';"

        sqlQ = sqlquery % {
            'ids': str(
                Symbolids[0]),
            'fromdate': Fromdate.strftime("%Y-%m-%d"),
            'todate': Todate.strftime("%Y-%m-%d")}

    else:
        sqlquery = "SELECT * FROM dataapp_stockprice as dsp \
        WHERE dsp.\"Symbol_id\" IN %(ids)s AND dsp.\"Date\" \
        BETWEEN '%(fromdate)s' AND '%(todate)s';"

        sqlQ = sqlquery % {
            'ids': str(
                tuple(Symbolids)),
            'fromdate': Fromdate.strftime("%Y-%m-%d"),
            'todate': Todate.strftime("%Y-%m-%d")}

    df = pd.read_sql(sqlQ, connections[dtamd.Stockprice._DATABASE])
    df = StockDataFrame_sanitize(df, standardize=standardize)

    if format == 'list':
        L = []
        for symbid in Symbolids:
            dp = df[df['Symbol_id'] == symbid].copy()
            if addcols is not None:
                dp = addindicators(dp, addcols)
            L.append(dp)
        return L

    elif format == 'dict':
        D = {}
        for symbid in Symbolids:
            dp = df[df['Symbol_id'] == symbid].copy()
            if addcols is not None:
                dp = addindicators(dp, addcols)
            D[symbid] = dp
        return D

    elif format == 'concat':
        return df
