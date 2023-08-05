

class Quote(dict):
    def __init__(self, *args):
        super().__init__(*args)

        self.Ask: dict = {}
        self.Bid: dict = {}

    def AskPrice(self):
        return super().get('AskPrice', None)

    def AskVolSum(self):
        return super().get('AskVolSum', None)

    def AskVolume(self):
        return super().get('AskVolume', None)

    def BidPrice(self):
        return super().get('BidPrice', None)

    def BidVolSum(self):
        return super().get('BidVolSum', None)

    def BidVolume(self):
        return super().get('BidVolume', None)

    def Code(self):
        return super().get('Code', None)

    def Date(self):
        return super().get('Date', None)

    def DiffAskVol(self):
        return super().get('DiffAskVol', None)

    def DiffAskVolSum(self):
        return super().get('DiffAskVolSum', None)

    def DiffBidVol(self):
        return super().get('DiffBidVol', None)

    def DiffBidVolSum(self):
        return super().get('DiffBidVolSum', None)

    def FirstDerivedAskPrice(self):
        return super().get('FirstDerivedAskPrice', None)

    def FirstDerivedAskVolume(self):
        return super().get('FirstDerivedAskVolume', None)

    def FirstDerivedBidPrice(self):
        return super().get('FirstDerivedBidPrice', None)

    def FirstDerivedBidVolume(self):
        return super().get('FirstDerivedBidVolume', None)

    def TargetKindPrice(self):
        return super().get('TargetKindPrice', None)

    def Time(self):
        return super().get('Time', None)

    def Simtrade(self):
        return super().get('Simtrade', None)

    def zipAsk(self):
        self.Ask = dict(zip(self.AskPrice(), self.AskVolume()))

    def zipBid(self):
        self.Bid = dict(zip(self.BidPrice(), self.BidVolume()))


# {"AmountSum": [65246500.0],
#  "Close": [415.5],
#  "Date": "2022/06/07",
#  "TickType": [2],
#  "Time": "09:01:41.845465",
#  "VolSum": [156],
#  "Volume": [3]}
class Market(dict):
    def Amount(self):
        return super().get('Amount', None)

    def AmountSum(self):
        return super().get('AmountSum', None)

    def AvgPrice(self):
        return super().get('AvgPrice', None)

    def Close(self):
        return super().get('Close', None)

    def Code(self):
        return super().get('Code', None)

    def Date(self):
        return super().get('Date', None)

    def DiffPrice(self):
        return super().get('DiffPrice', None)

    def DiffRate(self):
        return super().get('DiffRate', None)

    def DiffType(self):
        return super().get('DiffType', None)

    def High(self):
        return super().get('High', None)

    def Low(self):
        return super().get('Low', None)

    def Open(self):
        return super().get('Open', None)

    def TargetKindPrice(self):
        return super().get('TargetKindPrice', None)

    def TickType(self):
        return super().get('TickType', None)

    def Time(self):
        return super().get('Time', None)

    def TradeAskVolSum(self):
        return super().get('TradeAskVolSum', None)

    def TradeBidVolSum(self):
        return super().get('TradeBidVolSum', None)

    def VolSum(self):
        return super().get('VolSum', None)

    def Volume(self):
        return super().get('Volume', None)

    def Simtrade(self):
        return super().get('Simtrade', None)
