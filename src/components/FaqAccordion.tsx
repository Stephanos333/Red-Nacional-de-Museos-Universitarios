import React, { useMemo, useState } from 'react';
import { ChevronDown, Search, CheckCircle2, X } from 'lucide-react';

export const FAQ_CATEGORIAS = [
  'Marco Legal, Naturaleza y Vinculación',
  'Autonomía, Compromisos y Gratuidad',
  'Dinámica de Trabajo, Beneficios y Caracterización',
] as const;

export type FaqCategoria = (typeof FAQ_CATEGORIAS)[number];

export interface FaqItem {
  id: number;
  categoria: FaqCategoria;
  pregunta: string;
  respuesta: string;
}

interface FaqAccordionProps {
  items: FaqItem[];
}

const TODAS = 'Todas' as const;
type Filtro = FaqCategoria | typeof TODAS;

export const FaqAccordion: React.FC<FaqAccordionProps> = ({ items }) => {
  const [openIds, setOpenIds] = useState<number[]>(items.length ? [items[0].id] : []);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoria, setCategoria] = useState<Filtro>(TODAS);

  const toggleItem = (id: number) => {
    setOpenIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  const filteredItems = useMemo(() => {
    const q = searchTerm.toLowerCase().trim();
    return items.filter((item) => {
      if (categoria !== TODAS && item.categoria !== categoria) return false;
      if (!q) return true;
      return item.pregunta.toLowerCase().includes(q) || item.respuesta.toLowerCase().includes(q);
    });
  }, [items, searchTerm, categoria]);

  const grupos = FAQ_CATEGORIAS.map((cat) => ({
    categoria: cat,
    items: filteredItems.filter((i) => i.categoria === cat),
  })).filter((g) => g.items.length > 0);

  const countFor = (cat: Filtro) => (cat === TODAS ? items.length : items.filter((i) => i.categoria === cat).length);

  return (
    <div className="space-y-6">
      {/* Selector de categoría */}
      <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar preguntas por categoría">
        {([TODAS, ...FAQ_CATEGORIAS] as Filtro[]).map((cat) => {
          const active = categoria === cat;
          return (
            <button
              key={cat}
              type="button"
              onClick={() => setCategoria(cat)}
              aria-pressed={active}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-colors ${
                active
                  ? 'bg-brand-burgundy-800 text-white border-brand-burgundy-800 shadow-sm'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-brand-burgundy-200 hover:text-brand-burgundy-800'
              }`}
            >
              {cat} ({countFor(cat)})
            </button>
          );
        })}
      </div>

      {/* Búsqueda y controles */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-4 rounded-2xl border border-gray-200 shadow-sm">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar en preguntas frecuentes..."
            aria-label="Buscar en preguntas frecuentes"
            className="w-full pl-9 pr-8 py-2 rounded-xl border border-gray-200 text-xs focus:border-brand-burgundy-700 focus:ring-1 focus:ring-brand-burgundy-700 bg-gray-50"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              aria-label="Limpiar búsqueda"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={() => setOpenIds(filteredItems.map((i) => i.id))}
            className="px-3 py-1.5 rounded-lg border border-gray-200 text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors"
          >
            Desplegar todas
          </button>
          <button
            onClick={() => setOpenIds([])}
            className="px-3 py-1.5 rounded-lg border border-gray-200 text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors"
          >
            Colapsar todas
          </button>
        </div>
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-12 bg-white rounded-2xl border border-gray-200 p-6 text-gray-500 text-sm">
          No se encontraron preguntas que coincidan con &quot;{searchTerm}&quot;.
        </div>
      )}

      {/* Preguntas agrupadas por categoría */}
      {grupos.map((grupo) => (
        <section key={grupo.categoria} className="space-y-3.5" aria-labelledby={`faq-cat-${FAQ_CATEGORIAS.indexOf(grupo.categoria)}`}>
          <h2
            id={`faq-cat-${FAQ_CATEGORIAS.indexOf(grupo.categoria)}`}
            className="text-sm font-bold uppercase tracking-wider text-brand-burgundy-800 pt-2"
          >
            {grupo.categoria}
          </h2>
          {grupo.items.map((item) => {
            const isOpen = openIds.includes(item.id);
            const panelId = `faq-panel-${item.id}`;
            return (
              <div
                key={item.id}
                className={`rounded-2xl border transition-all duration-200 overflow-hidden ${
                  isOpen ? 'bg-white border-brand-burgundy-200 shadow-sm' : 'bg-white/80 border-gray-200/90 hover:border-gray-300'
                }`}
              >
                <button
                  type="button"
                  onClick={() => toggleItem(item.id)}
                  aria-expanded={isOpen}
                  aria-controls={panelId}
                  className="w-full px-6 py-5 text-left flex items-start justify-between gap-4 cursor-pointer"
                >
                  <div className="flex items-start gap-3.5">
                    <span className="flex-shrink-0 w-7 h-7 rounded-lg bg-brand-burgundy-50 text-brand-burgundy-800 text-xs font-bold flex items-center justify-center mt-0.5 border border-brand-burgundy-100">
                      {item.id}
                    </span>
                    <span className="text-base font-serif font-bold text-gray-900 leading-snug">{item.pregunta}</span>
                  </div>
                  <div
                    className={`p-1 rounded-full text-gray-400 transition-transform duration-200 shrink-0 ${
                      isOpen ? 'rotate-180 text-brand-burgundy-800 bg-brand-burgundy-50' : ''
                    }`}
                  >
                    <ChevronDown className="w-5 h-5" />
                  </div>
                </button>

                {isOpen && (
                  <div id={panelId} className="px-6 pb-6 pt-1 text-sm text-gray-700 leading-relaxed border-t border-gray-100 space-y-3">
                    {item.respuesta.split('\n\n').map((paragraph, idx) => (
                      <div key={idx}>
                        {paragraph.startsWith('- ') ? (
                          <ul className="space-y-1.5 pl-2 mt-2">
                            {paragraph.split('\n').map((line, lIdx) => (
                              <li key={lIdx} className="flex items-start gap-2 text-xs sm:text-sm text-gray-600">
                                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                                <span>{line.replace(/^- /, '')}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="whitespace-pre-line text-xs sm:text-sm text-gray-600">{paragraph}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </section>
      ))}
    </div>
  );
};
