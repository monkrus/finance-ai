import {
  adaptCompanyProfile,
  adaptQuote,
  adaptHistoricalSeries,
  adaptMarketIndex,
  adaptSearchResult,
  adaptCompanyNews,
  CompanyProfileDTO,
  StockQuoteDTO,
  HistoricalPriceSeriesDTO,
  MarketIndexDTO,
  CompanySearchResultDTO,
  MarketNewsDTO,
} from '@/features/market/api/adapters';

describe('market adapters', () => {
  describe('adaptCompanyProfile', () => {
    it('maps snake_case to camelCase view model', () => {
      const dto: CompanyProfileDTO = {
        ticker: 'AAPL',
        company_name: 'Apple Inc.',
        exchange: 'NASDAQ',
        industry: 'Consumer Electronics',
        sector: 'Technology',
        website: 'https://apple.com',
        description: 'Designs phones.',
        ceo: 'Tim Cook',
        market_cap: 3.2e12,
        image: 'https://logo.png',
      };
      const vm = adaptCompanyProfile(dto);
      expect(vm.companyName).toBe('Apple Inc.');
      expect(vm.logo).toBe('https://logo.png');
      expect(vm.marketCap).toBe(3.2e12);
      expect(vm.website).toBe('https://apple.com');
    });

    it('defaults missing optional fields so components never crash', () => {
      const vm = adaptCompanyProfile({ ticker: 'X', company_name: 'X Corp' });
      // Components call .replace() on website and divide marketCap — must be safe.
      expect(vm.website).toBe('');
      expect(vm.description).toBe('');
      expect(vm.logo).toBe('');
      expect(vm.marketCap).toBe(0);
      expect(vm.employees).toBe(0);
      expect(vm.enterpriseValue).toBe(0);
    });
  });

  describe('adaptQuote', () => {
    it('maps quote fields and defaults nulls to 0', () => {
      const dto: StockQuoteDTO = { ticker: 'AAPL', price: 200, change_percent: 1.5 };
      const vm = adaptQuote(dto);
      expect(vm.price).toBe(200);
      expect(vm.changePercent).toBe(1.5);
      expect(vm.change).toBe(0);
      expect(vm.volume).toBe(0);
    });
  });

  describe('adaptHistoricalSeries', () => {
    it('unwraps prices[] and maps date -> time', () => {
      const dto: HistoricalPriceSeriesDTO = {
        ticker: 'AAPL',
        prices: [{ date: '2026-01-02', open: 1, high: 2, low: 0.5, close: 1.5, volume: 100 }],
      };
      const rows = adaptHistoricalSeries(dto);
      expect(rows).toHaveLength(1);
      expect(rows[0].time).toBe('2026-01-02');
      expect(rows[0].close).toBe(1.5);
    });

    it('returns [] when prices missing', () => {
      expect(adaptHistoricalSeries({ ticker: 'X' } as HistoricalPriceSeriesDTO)).toEqual([]);
    });
  });

  describe('adaptMarketIndex', () => {
    it('maps change_percent, empty sparkline and derives trend', () => {
      const up: MarketIndexDTO = { symbol: '^GSPC', name: 'S&P 500', price: 5000, change_percent: 0.8 };
      expect(adaptMarketIndex(up).trend).toBe('up');
      expect(adaptMarketIndex(up).changePercent).toBe(0.8);
      expect(adaptMarketIndex(up).sparkline).toEqual([]);

      const down: MarketIndexDTO = { symbol: 'X', name: 'X', price: 1, change_percent: -1 };
      expect(adaptMarketIndex(down).trend).toBe('down');

      const flat: MarketIndexDTO = { symbol: 'Y', name: 'Y', price: 1 };
      expect(adaptMarketIndex(flat).trend).toBe('neutral');
      expect(adaptMarketIndex(flat).changePercent).toBe(0);
    });
  });

  describe('adaptSearchResult', () => {
    it('maps ticker -> symbol and defaults type', () => {
      const dto: CompanySearchResultDTO = { ticker: 'MSFT', name: 'Microsoft', exchange: 'NASDAQ' };
      const vm = adaptSearchResult(dto);
      expect(vm.symbol).toBe('MSFT');
      expect(vm.name).toBe('Microsoft');
      expect(vm.type).toBe('Stock');
    });

    it('defaults missing name/exchange', () => {
      const vm = adaptSearchResult({ ticker: 'T' });
      expect(vm.name).toBe('');
      expect(vm.exchange).toBe('');
    });
  });

  describe('adaptCompanyNews', () => {
    it('maps to NewsItem with neutral defaults', () => {
      const dto: MarketNewsDTO = {
        id: '1',
        symbol: 'AAPL',
        title: 'Apple ships',
        published_at: '2026-07-18T00:00:00Z',
        source: 'Reuters',
        url: 'https://x.com',
      };
      const vm = adaptCompanyNews(dto);
      expect(vm.publishedAt).toBe('2026-07-18T00:00:00Z');
      expect(vm.summary).toBe('');
      expect(vm.sentiment).toBe('neutral');
      expect(vm.importance).toBe('medium');
    });
  });
});
