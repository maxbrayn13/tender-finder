import React, { useState, useEffect, useMemo } from 'react';

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Client
const api = {
  getLots: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_URL}/lots?${query}`);
    return res.json();
  },
  getLot: async (id) => {
    const res = await fetch(`${API_URL}/lots/${id}`);
    return res.json();
  },
  searchLots: async (data) => {
    const res = await fetch(`${API_URL}/lots/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },
  searchByBudget: async (data) => {
    const res = await fetch(`${API_URL}/lots/search-by-budget`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },
  searchByMargin: async (data) => {
    const res = await fetch(`${API_URL}/lots/search-by-margin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },
  getStats: async () => {
    const res = await fetch(`${API_URL}/stats`);
    return res.json();
  },
  getCategories: async () => {
    const res = await fetch(`${API_URL}/categories`);
    return res.json();
  },
};

// Utils
const fmt = (n) => new Intl.NumberFormat('ru-RU').format(Math.round(n || 0));
const fmtShort = (n) => {
  if (!n) return '0';
  if (n >= 1e6) return `${(n/1e6).toFixed(1)}M`;
  if (n >= 1e3) return `${(n/1e3).toFixed(0)}K`;
  return n.toString();
};

// Icons (simplified)
const Icon = ({ type }) => {
  const icons = {
    search: '🔍',
    heart: '❤️',
    heartEmpty: '🤍',
    fire: '🔥',
    box: '📦',
    wallet: '💰',
    trend: '📈',
    chart: '📊',
    user: '👤',
    logout: '🚪',
    arrow: '→',
    arrowLeft: '←',
    check: '✅',
    x: '✕',
  };
  return <span className="inline-block">{icons[type] || '•'}</span>;
};

// Components
const Button = ({ children, variant = 'primary', loading, disabled, className = '', ...props }) => {
  const variants = {
    primary: 'bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-lg',
    secondary: 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 shadow-sm',
    ghost: 'bg-transparent hover:bg-gray-100 text-gray-600',
  };
  return (
    <button 
      disabled={loading || disabled}
      className={`px-5 py-2.5 rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {loading ? '⏳' : children}
    </button>
  );
};

const Card = ({ children, className = '', hover = true, ...props }) => (
  <div 
    className={`bg-white rounded-2xl border border-gray-100 ${hover ? 'hover:shadow-xl transition-all duration-300' : ''} ${className}`}
    {...props}
  >
    {children}
  </div>
);

const Badge = ({ children, color = 'gray' }) => {
  const colors = {
    gray: 'bg-gray-100 text-gray-600',
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-emerald-50 text-emerald-600',
    orange: 'bg-amber-50 text-amber-600',
    red: 'bg-rose-50 text-rose-600',
    gradient: 'bg-gradient-to-r from-amber-500 to-orange-500 text-white',
  };
  return <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-semibold rounded-lg ${colors[color]}`}>{children}</span>;
};

const Spinner = () => <div className="w-7 h-7 border-2 border-violet-200 border-t-violet-600 rounded-full animate-spin"></div>;

// Product Card
const ProductCard = ({ product, onView, onFavorite, isFavorite, detailed = false }) => {
  const stats = product.stats || {};
  const isHot = stats.margin_percent >= 100;

  return (
    <Card className={`overflow-hidden ${isHot ? 'ring-2 ring-amber-200' : ''}`}>
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex flex-wrap gap-2">
            {isHot && <Badge color="gradient"><Icon type="fire" /> HOT</Badge>}
          </div>
          {onFavorite && (
            <button onClick={(e) => { e.stopPropagation(); onFavorite(product.id); }} className={`p-2 rounded-xl transition-all ${isFavorite ? 'bg-rose-50 text-rose-500' : 'bg-gray-50 text-gray-300'}`}>
              <Icon type={isFavorite ? 'heart' : 'heartEmpty'} />
            </button>
          )}
        </div>
        
        <Badge color="gray">{product.lot_number}</Badge>
        
        <h3 className="font-semibold text-gray-900 mt-2 mb-3 line-clamp-2 min-h-[48px] hover:text-violet-600 cursor-pointer transition" onClick={() => onView(product)}>
          {product.simplified_name || product.original_name}
        </h3>
        
        <div className="mb-4">
          <Badge color="blue">{product.category || 'Разное'}</Badge>
        </div>
        
        {detailed && stats ? (
          <div className="space-y-2 p-4 bg-gradient-to-br from-slate-50 to-violet-50/30 rounded-xl mb-4 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Кол-во:</span><span className="font-semibold">{fmt(product.quantity)} {product.unit}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">💰 Себестоимость:</span><span className="font-bold text-violet-600">{fmt(stats.total_expense)}₸</span></div>
            <div className="flex justify-between"><span className="text-gray-500">💵 Выручка:</span><span className="font-semibold">{fmt(stats.revenue)}₸</span></div>
            <div className="flex justify-between pt-2 border-t border-gray-200"><span className="text-gray-500">📈 Прибыль:</span><span className="font-bold text-emerald-600">+{fmt(stats.profit)}₸</span></div>
            <div className="flex justify-between"><span className="text-gray-500">🎯 ROI:</span><span className="font-bold text-amber-600">+{stats.roi}%</span></div>
          </div>
        ) : (
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm"><span className="text-gray-500">Тендер:</span><span className="font-bold">{fmt(product.tender_price)}₸</span></div>
            {stats.best_price && (
              <>
                <div className="flex justify-between text-sm"><span className="text-gray-500">Лучшая:</span><span className="font-bold text-emerald-600">{fmt(stats.best_price)}₸</span></div>
                <div className="flex justify-between text-sm pt-2 border-t"><span className="text-gray-500">Маржа:</span><span className={`text-lg font-bold ${isHot ? 'text-amber-500' : 'text-emerald-600'}`}>+{stats.margin_percent}%</span></div>
              </>
            )}
          </div>
        )}
        
        <Button onClick={() => onView(product)} className="w-full">Подробнее <Icon type="arrow" /></Button>
      </div>
    </Card>
  );
};

// Main App
export default function TenderFinderApp() {
  const [page, setPage] = useState('home');
  const [user, setUser] = useState(null);
  const [product, setProduct] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  
  const [lots, setLots] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  
  const [budgetInput, setBudgetInput] = useState('');
  const [marginInput, setMarginInput] = useState('');
  const [calcResults, setCalcResults] = useState({ type: null, data: [] });

  // Load data
  useEffect(() => {
    loadStats();
    loadCategories();
    if (page === 'catalog') loadLots();
  }, [page]);

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await api.getCategories();
      setCategories(['all', ...data]);
    } catch (err) {
      console.error('Error loading categories:', err);
    }
  };

  const loadLots = async () => {
    setLoading(true);
    try {
      const params = { limit: 50 };
      if (category && category !== 'all') params.category = category;
      if (search) params.search = search;
      const data = await api.getLots(params);
      setLots(data);
    } catch (err) {
      console.error('Error loading lots:', err);
    }
    setLoading(false);
  };

  const searchByBudget = async () => {
    const budget = parseFloat(budgetInput.replace(/\D/g, ''));
    if (!budget) return;
    setLoading(true);
    try {
      const data = await api.searchByBudget({ budget });
      setCalcResults({ type: 'budget', data: data.results, query: budget });
    } catch (err) {
      console.error('Error:', err);
    }
    setLoading(false);
  };

  const searchByMargin = async () => {
    const target = parseFloat(marginInput.replace(/\D/g, ''));
    if (!target) return;
    setLoading(true);
    try {
      const data = await api.searchByMargin({ target_margin: target });
      setCalcResults({ type: 'margin', data: data.results, query: target });
    } catch (err) {
      console.error('Error:', err);
    }
    setLoading(false);
  };

  const navigate = (p, data = null) => {
    setPage(p);
    if (data) setProduct(data);
    window.scrollTo(0, 0);
  };

  const toggleFav = (id) => {
    if (!user) return navigate('auth');
    setFavorites(f => f.includes(id) ? f.filter(x => x !== id) : [...f, id]);
  };

  // Header
  const Header = () => (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => navigate('home')}>
            <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">TenderFinder</span>
          </div>
          
          <nav className="hidden md:flex items-center space-x-4">
            <button onClick={() => navigate('home')} className={`px-4 py-2 rounded-lg font-medium transition ${page === 'home' ? 'bg-violet-50 text-violet-600' : 'text-gray-600'}`}>Главная</button>
            <button onClick={() => navigate('catalog')} className={`px-4 py-2 rounded-lg font-medium transition ${page === 'catalog' ? 'bg-violet-50 text-violet-600' : 'text-gray-600'}`}>Каталог</button>
            {user && <button onClick={() => navigate('profile')} className={`px-4 py-2 rounded-lg font-medium transition ${page === 'profile' ? 'bg-violet-50 text-violet-600' : 'text-gray-600'}`}>Кабинет</button>}
          </nav>
          
          <div>
            {user ? (
              <div className="flex items-center space-x-3">
                <span className="hidden sm:inline text-sm font-medium text-gray-700">{user.name}</span>
                <button onClick={() => { setUser(null); navigate('home'); }} className="p-2 hover:bg-gray-100 rounded-lg transition">
                  <Icon type="logout" />
                </button>
              </div>
            ) : (
              <Button onClick={() => setUser({ name: 'Demo User', email: 'demo@test.com' })}>Войти</Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );

  // Home Page
  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-indigo-600 to-purple-700 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold mb-6">
            Найди товары для тендеров
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-amber-300 to-yellow-300">по лучшим ценам</span>
          </h1>
          <p className="text-xl text-indigo-100 mb-10">Сравниваем цены на маркетплейсах Казахстана и Китая</p>
          
          <div className="max-w-xl mx-auto mb-8">
            <div className="flex bg-white rounded-2xl overflow-hidden shadow-2xl">
              <input type="text" placeholder="Поиск..." value={search} onChange={(e) => setSearch(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && navigate('catalog')} className="flex-1 px-5 py-4 outline-none text-gray-700" />
              <button onClick={() => navigate('catalog')} className="bg-gradient-to-r from-violet-500 to-indigo-600 text-white px-8 font-semibold">
                <Icon type="search" /> Найти
              </button>
            </div>
          </div>
          
          {stats.total_lots && (
            <div className="flex justify-center gap-6 text-center">
              <div className="bg-white/10 backdrop-blur rounded-xl px-6 py-4"><div className="text-3xl font-bold">{stats.total_lots}</div><div className="text-blue-200 text-sm">Лотов</div></div>
              <div className="bg-white/10 backdrop-blur rounded-xl px-6 py-4"><div className="text-2xl font-bold">{fmtShort(stats.total_sum)}₸</div><div className="text-blue-200 text-sm">Сумма</div></div>
              <div className="bg-white/10 backdrop-blur rounded-xl px-6 py-4"><div className="text-3xl font-bold">{stats.avg_margin}%</div><div className="text-blue-200 text-sm">Маржа</div></div>
            </div>
          )}
        </div>
      </section>

      {/* Calculators */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">🎯 Умный поиск лотов</h2>
          <p className="text-gray-500">Найдите идеальные сделки под ваш бюджет или желаемую прибыль</p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <Card className="p-8 border-2 border-emerald-100">
            <div className="flex items-center space-x-4 mb-6">
              <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg text-3xl">
                <Icon type="wallet" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">По бюджету</h3>
                <p className="text-sm text-gray-500">Лоты под вашу сумму</p>
              </div>
            </div>
            <div className="space-y-4">
              <input type="text" value={budgetInput ? fmt(budgetInput) : ''} onChange={(e) => setBudgetInput(e.target.value.replace(/\D/g, ''))} placeholder="700 000" className="w-full px-5 py-4 text-xl font-bold border-2 border-emerald-200 rounded-2xl outline-none focus:border-emerald-500" />
              <Button onClick={searchByBudget} loading={loading && calcResults.type === 'budget'} disabled={!budgetInput} className="w-full">
                <Icon type="search" /> Найти лоты
              </Button>
            </div>
          </Card>

          <Card className="p-8 border-2 border-amber-100">
            <div className="flex items-center space-x-4 mb-6">
              <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg text-3xl">
                <Icon type="trend" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">По прибыли</h3>
                <p className="text-sm text-gray-500">Лоты с желаемой маржой</p>
              </div>
            </div>
            <div className="space-y-4">
              <input type="text" value={marginInput ? fmt(marginInput) : ''} onChange={(e) => setMarginInput(e.target.value.replace(/\D/g, ''))} placeholder="1 500 000" className="w-full px-5 py-4 text-xl font-bold border-2 border-amber-200 rounded-2xl outline-none focus:border-amber-500" />
              <Button onClick={searchByMargin} loading={loading && calcResults.type === 'margin'} disabled={!marginInput} className="w-full">
                <Icon type="search" /> Найти лоты
              </Button>
            </div>
          </Card>
        </div>

        {calcResults.data.length > 0 && (
          <div className="mt-12">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-900">
                {calcResults.type === 'budget' ? '💰' : '📈'} Найдено {calcResults.data.length} лотов
              </h3>
              <Button variant="ghost" onClick={() => setCalcResults({ type: null, data: [] })}>
                <Icon type="x" /> Закрыть
              </Button>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {calcResults.data.map(p => <ProductCard key={p.id} product={p} onView={navigate} onFavorite={toggleFav} isFavorite={favorites.includes(p.id)} detailed />)}
            </div>
          </div>
        )}
      </section>
    </div>
  );

  // Catalog Page
  const CatalogPage = () => {
    useEffect(() => { loadLots(); }, [search, category]);

    return (
      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">📦 Каталог лотов</h1>
          
          <Card className="p-4 mb-8" hover={false}>
            <div className="flex flex-wrap gap-4">
              <input type="text" placeholder="Поиск..." value={search} onChange={(e) => setSearch(e.target.value)} className="flex-1 min-w-[250px] px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-violet-500" />
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="px-4 py-3 border border-gray-200 rounded-xl outline-none">
                {categories.map(c => <option key={c} value={c}>{c === 'all' ? 'Все' : c}</option>)}
              </select>
              <Button onClick={loadLots} loading={loading}><Icon type="search" /> Поиск</Button>
            </div>
          </Card>
          
          {loading ? (
            <div className="flex justify-center py-20"><Spinner /></div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {lots.map(p => <ProductCard key={p.id} product={p} onView={() => navigate('product', p)} onFavorite={toggleFav} isFavorite={favorites.includes(p.id)} />)}
            </div>
          )}
          
          {!loading && lots.length === 0 && (
            <div className="text-center py-20 text-gray-500">
              <div className="text-6xl mb-4"><Icon type="search" /></div>
              <p>Ничего не найдено</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Product Page
  const ProductPage = () => {
    if (!product) return null;
    const stats = product.stats || {};

    return (
      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-5xl mx-auto px-4">
          <Button variant="ghost" onClick={() => navigate('catalog')} className="mb-6">
            <Icon type="arrowLeft" /> Назад
          </Button>
          
          <Card className="p-8 mb-6" hover={false}>
            <div className="mb-6">
              <Badge color="gray">{product.lot_number}</Badge>
              {stats.margin_percent >= 100 && <Badge color="gradient" className="ml-2"><Icon type="fire" /> HOT</Badge>}
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-6">{product.simplified_name || product.original_name}</h1>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-gray-700 mb-4"><Icon type="box" /> О тендере</h3>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b"><span className="text-gray-500">Заказчик</span><span className="font-medium text-right">{product.customer}</span></div>
                  <div className="flex justify-between py-2 border-b"><span className="text-gray-500">Категория</span><span className="font-medium">{product.category || 'Разное'}</span></div>
                  <div className="flex justify-between py-2 border-b"><span className="text-gray-500">Количество</span><span className="font-medium">{fmt(product.quantity)} {product.unit}</span></div>
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-violet-50 to-indigo-50 rounded-2xl p-6">
                <h3 className="font-semibold text-gray-700 mb-4">💰 Ценовая аналитика</h3>
                <div className="space-y-3">
                  <div className="flex justify-between"><span className="text-gray-500">Тендер:</span><span className="text-2xl font-bold">{fmt(product.tender_price)}₸</span></div>
                  {stats.best_price && (
                    <>
                      <div className="flex justify-between"><span className="text-gray-500">Лучшая:</span><span className="text-2xl font-bold text-emerald-600">{fmt(stats.best_price)}₸</span></div>
                      <div className="flex justify-between pt-3 border-t"><span className="text-gray-500">Маржа:</span><span className="text-2xl font-bold text-amber-500">+{stats.margin_percent}%</span></div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </Card>
          
          {stats.profit && (
            <div className="bg-gradient-to-br from-violet-600 to-indigo-700 rounded-2xl p-8 text-white">
              <h3 className="font-bold text-xl mb-6"><Icon type="chart" /> Калькулятор прибыли</h3>
              <div className="bg-white/10 backdrop-blur rounded-xl p-6 space-y-4">
                <div className="flex justify-between"><span>Себестоимость:</span><strong>{fmt(stats.total_expense)}₸</strong></div>
                <div className="flex justify-between"><span>Выручка:</span><strong>{fmt(stats.revenue)}₸</strong></div>
                <div className="flex justify-between pt-4 border-t-2 border-white/30"><span className="text-lg">📈 Прибыль:</span><span className="text-3xl font-bold text-emerald-300">+{fmt(stats.profit)}₸</span></div>
                <div className="flex justify-between"><span>🎯 ROI:</span><span className="text-2xl font-bold text-amber-300">+{stats.roi}%</span></div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      {page === 'home' && <HomePage />}
      {page === 'catalog' && <CatalogPage />}
      {page === 'product' && <ProductPage />}
    </div>
  );
}
