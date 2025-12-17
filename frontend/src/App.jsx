import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = {
  getLots: (params) => fetch(`${API_URL}/lots?${new URLSearchParams(params)}`).then(r => r.json()),
  getLot: (id) => fetch(`${API_URL}/lots/${id}`).then(r => r.json()),
  searchLots: (data) => fetch(`${API_URL}/lots/search`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),
  searchByBudget: (data) => fetch(`${API_URL}/lots/search-by-budget`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),
  searchByMargin: (data) => fetch(`${API_URL}/lots/search-by-margin`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),
  getStats: () => fetch(`${API_URL}/stats`).then(r => r.json()),
  getCategories: () => fetch(`${API_URL}/categories`).then(r => r.json())
}

const fmt = (n) => new Intl.NumberFormat('ru-RU').format(n)
const fmtShort = (n) => n >= 1e6 ? `${(n/1e6).toFixed(1)}M` : n >= 1e3 ? `${(n/1e3).toFixed(0)}K` : fmt(n)

function App() {
  const [page, setPage] = useState('home')
  const [lots, setLots] = useState([])
  const [categories, setCategories] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [budgetInput, setBudgetInput] = useState('')
  const [marginInput, setMarginInput] = useState('')
  const [calcResults, setCalcResults] = useState(null)
  const [product, setProduct] = useState(null)

  useEffect(() => {
    api.getCategories().then(data => setCategories(data.categories))
    api.getStats().then(setStats)
  }, [])

  const handleBudgetSearch = async () => {
    setLoading(true)
    const data = await api.searchByBudget({ budget: parseFloat(budgetInput) })
    setCalcResults(data)
    setLoading(false)
  }

  const handleMarginSearch = async () => {
    setLoading(true)
    const data = await api.searchByMargin({ target_margin: parseFloat(marginInput) })
    setCalcResults(data)
    setLoading(false)
  }

  const loadCatalog = async () => {
    setLoading(true)
    const data = await api.getLots({ limit: 100, category, search })
    setLots(data.results)
    setLoading(false)
  }

  const viewProduct = async (id) => {
    setLoading(true)
    const data = await api.getLot(id)
    setProduct(data)
    setPage('product')
    setLoading(false)
  }

  useEffect(() => {
    if (page === 'catalog') loadCatalog()
  }, [page, category])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <nav className="bg-black/30 backdrop-blur border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center font-bold text-xl">T</div>
            <span className="font-bold text-xl text-white">TenderFinder</span>
          </div>
          <div className="flex gap-4">
            <button onClick={() => {setPage('home'); setCalcResults(null)}} className="px-4 py-2 text-white/80 hover:text-white">Главная</button>
            <button onClick={() => setPage('catalog')} className="px-4 py-2 text-white/80 hover:text-white">Каталог</button>
          </div>
        </div>
      </nav>

      {page === 'home' && (
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
              Найдите выгодные госзакупки
            </h1>
            <p className="text-xl text-white/60 max-w-2xl mx-auto">
              Автоматический расчёт прибыли и ROI для тендеров Казахстана
            </p>
          </div>

          {stats && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
              <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
                <div className="text-white/60 text-sm mb-1">Всего лотов</div>
                <div className="text-3xl font-bold text-white">{stats.total_lots}</div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
                <div className="text-white/60 text-sm mb-1">Общая сумма</div>
                <div className="text-3xl font-bold text-white">{fmtShort(stats.total_sum)}₸</div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
                <div className="text-white/60 text-sm mb-1">Средняя маржа</div>
                <div className="text-3xl font-bold text-emerald-400">{stats.avg_margin}%</div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
                <div className="text-white/60 text-sm mb-1">Горячие лоты</div>
                <div className="text-3xl font-bold text-orange-400">{stats.hot_deals}</div>
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <div className="bg-white/10 backdrop-blur rounded-2xl p-8 border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-4">💰 Поиск по бюджету</h3>
              <p className="text-white/60 mb-6">Найдите лоты под ваш бюджет</p>
              <input
                type="number"
                placeholder="Введите бюджет (₸)"
                value={budgetInput}
                onChange={(e) => setBudgetInput(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-white/40 mb-4"
              />
              <button
                onClick={handleBudgetSearch}
                disabled={loading}
                className="w-full px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl font-medium hover:from-violet-700 hover:to-purple-700 disabled:opacity-50"
              >
                {loading ? 'Поиск...' : 'Найти лоты'}
              </button>
            </div>

            <div className="bg-white/10 backdrop-blur rounded-2xl p-8 border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-4">📈 Поиск по марже</h3>
              <p className="text-white/60 mb-6">Найдите лоты с нужной прибылью</p>
              <input
                type="number"
                placeholder="Желаемая прибыль (₸)"
                value={marginInput}
                onChange={(e) => setMarginInput(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-white/40 mb-4"
              />
              <button
                onClick={handleMarginSearch}
                disabled={loading}
                className="w-full px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl font-medium hover:from-emerald-700 hover:to-teal-700 disabled:opacity-50"
              >
                {loading ? 'Поиск...' : 'Найти лоты'}
              </button>
            </div>
          </div>

          {calcResults && (
            <div className="bg-white/10 backdrop-blur rounded-2xl p-8 border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-6">Результаты поиска: {calcResults.total} лотов</h3>
              <div className="grid gap-4">
                {calcResults.results.slice(0, 10).map((lot, i) => (
                  <div key={i} onClick={() => viewProduct(lot.id)} className="bg-white/5 rounded-xl p-6 border border-white/10 hover:border-violet-500/50 cursor-pointer transition">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h4 className="text-white font-medium mb-1">{lot.simplified_name}</h4>
                        <div className="text-white/60 text-sm">{lot.lot_number}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-emerald-400">{fmt(lot.stats.profit)}₸</div>
                        <div className="text-white/60 text-sm">прибыль</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <div className="text-white/40">ROI</div>
                        <div className="text-white font-medium">{lot.stats.roi}%</div>
                      </div>
                      <div>
                        <div className="text-white/40">Себестоимость</div>
                        <div className="text-white font-medium">{fmt(lot.stats.total_expense)}₸</div>
                      </div>
                      <div>
                        <div className="text-white/40">Маржа</div>
                        <div className="text-white font-medium">{lot.stats.margin_percent}%</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {page === 'catalog' && (
        <div className="max-w-7xl mx-auto px-4 py-12">
          <h2 className="text-3xl font-bold text-white mb-8">Каталог лотов</h2>
          
          <div className="flex gap-4 mb-8">
            <input
              type="text"
              placeholder="Поиск..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && loadCatalog()}
              className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/40"
            />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white"
            >
              <option value="">Все категории</option>
              {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
            <button
              onClick={loadCatalog}
              className="px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl font-medium hover:from-violet-700 hover:to-purple-700"
            >
              Поиск
            </button>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {lots.map(lot => (
              <div key={lot.id} onClick={() => viewProduct(lot.id)} className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20 hover:border-violet-500/50 cursor-pointer transition">
                <h3 className="text-white font-medium mb-2 line-clamp-2">{lot.simplified_name}</h3>
                <div className="text-white/60 text-sm mb-4">{lot.category}</div>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-white/40 text-xs">Тендерная цена</div>
                    <div className="text-white font-bold">{fmt(lot.tender_price)}₸</div>
                  </div>
                  <div className="text-right">
                    <div className="text-white/40 text-xs">Количество</div>
                    <div className="text-white font-bold">{lot.quantity}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {page === 'product' && product && (
        <div className="max-w-4xl mx-auto px-4 py-12">
          <button onClick={() => setPage('catalog')} className="text-white/60 hover:text-white mb-6">← Назад</button>
          
          <div className="bg-white/10 backdrop-blur rounded-2xl p-8 border border-white/20 mb-6">
            <h2 className="text-3xl font-bold text-white mb-2">{product.simplified_name}</h2>
            <div className="text-white/60 mb-4">{product.lot_number}</div>
            <div className="inline-block px-3 py-1 bg-violet-500/20 text-violet-300 rounded-full text-sm">{product.category}</div>
          </div>

          {product.stats && (
            <div className="bg-white/10 backdrop-blur rounded-2xl p-8 border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-6">Финансовая аналитика</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="text-white/40 text-sm mb-1">Закупка</div>
                  <div className="text-2xl font-bold text-white">{fmt(product.stats.total_cost)}₸</div>
                </div>
                <div>
                  <div className="text-white/40 text-sm mb-1">Доставка</div>
                  <div className="text-2xl font-bold text-white">{fmt(product.stats.delivery_cost)}₸</div>
                </div>
                <div>
                  <div className="text-white/40 text-sm mb-1">Себестоимость</div>
                  <div className="text-2xl font-bold text-orange-400">{fmt(product.stats.total_expense)}₸</div>
                </div>
                <div>
                  <div className="text-white/40 text-sm mb-1">Выручка</div>
                  <div className="text-2xl font-bold text-blue-400">{fmt(product.stats.revenue)}₸</div>
                </div>
                <div>
                  <div className="text-white/40 text-sm mb-1">Прибыль</div>
                  <div className="text-3xl font-bold text-emerald-400">{fmt(product.stats.profit)}₸</div>
                </div>
                <div>
                  <div className="text-white/40 text-sm mb-1">ROI</div>
                  <div className="text-3xl font-bold text-purple-400">{product.stats.roi}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
