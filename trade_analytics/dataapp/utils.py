

def merge_df(df1, df2, on=['T', 'Symbol']):
    if 'Symbol' not in df1.columns:
        raise KeyError('df1 needs T and Symbol')

    if 'Symbol' not in df2.columns:
        raise KeyError('df2 needs T and Symbol')

    df1['T'] = df1.index
    df2['T'] = df2.index

    df = df1.merge(
        df2, how='left', on=[
            'T', 'Symbol'], suffixes=[
            '1c1', '2c2'])
    df.index = df['T'].copy()

    df.drop('T', axis=1, inplace=True)

    return df


def StockDataFrame_validate(
        df, columns=['Close', 'Open', 'High', 'Low', 'Volume']):
    for cc in columns:
        if cc not in df.columns:
            return False
    if not isinstance(df.index[0], pd.datetime):
        return False

    return True


def get_dateticks(From=pd.datetime(2010, 1, 1).date(),
                  To=pd.datetime.today().date(), ondays='EveryMonday'):
    D = {}
    D['EveryMonday'] = pd.date_range(
        start=pd.datetime(
            2010,
            1,
            1).date(),
        end=pd.datetime.today().date(),
        periods=None,
        freq='W-MON')
    D['EveryWednesday'] = pd.date_range(
        start=pd.datetime(
            2010,
            1,
            1).date(),
        end=pd.datetime.today().date(),
        periods=None,
        freq='W-WED')
    D['EveryFriday'] = pd.date_range(
        start=pd.datetime(
            2010,
            1,
            1).date(),
        end=pd.datetime.today().date(),
        periods=None,
        freq='W-FRI')
    D['EveryTueThu'] = list(
        pd.date_range(
            start=pd.datetime(
                2010,
                1,
                1).date(),
            end=pd.datetime.today().date(),
            periods=None,
            freq='W-TUE')) + list(
        pd.date_range(
            start=pd.datetime(
                2010,
                1,
                1).date(),
            end=pd.datetime.today().date(),
            periods=None,
            freq='W-THU'))

    D['EveryMonWedFri'] = list(
        set(list(D['EveryMonday']) + list(D['EveryWednesday']) + list(D['EveryFriday'])))
    D['EveryMonWedFri'] = sorted(D['EveryMonWedFri'])
    return map(lambda x: x.date(), D[ondays])


def Convert2date(T):
    """
    - Given a T, return the datetime object of type date
    - if T is string, first convert it
    - if T is datetime, convert to date
    """
    if isinstance(T, list) == True:
        pass
    elif isinstance(T, np.ndarray) == True:
        pass
    else:
        T = [T]
    # else:
    # 	raise TypeError('scalar, list or array expected')

    for i in range(len(T)):
        if isinstance(T[i], basestring):
            try:
                T[i] = pd.to_datetime(T[i]).date()
            except:
                pass

        elif isinstance(T[i], datetime.datetime) or isinstance(T[i], pd.datetime):
            T[i] = T[i].date()

        elif isinstance(T[i], pd.datetime.date) or isinstance(T[i], datetime.date):
            pass
        else:
            raise TypeError('No date found')

    if len(T) == 1:
        return T[0]
    else:
        return T


def setTradingdates():
    symbolids = stkmd.Stockmeta.objects.filter(
        Symbol__in=dtamd.TradingDates.CheckWith).values_list(
        'id', flat=True)
    df = GetStockData(
        symbolids,
        Fromdate=pd.datetime(
            2002,
            1,
            1).date(),
        Todate=pd.datetime.today().date(),
        format='concat',
        standardize=True,
        addcols=None)
    Trange = list(df.index.unique())
    # Trange.sorted()
    for TT in Trange:
        if dtamd.TradingDates.objects.filter(Date=TT).exists() == False:
            Td = dtamd.TradingDates(Date=TT)
            Td.save()


def getTradingdates():
    return dtamd.TradingDates.objects.all().values_list(
        'Date', flat=True).order_by('Date')
