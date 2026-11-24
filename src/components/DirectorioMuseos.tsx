import React, { useState, useMemo } from 'react';
import {
  Search,
  Building2,
  MapPin,
  Globe,
  Mail,
  Clock,
  Filter,
  X,
  LayoutGrid,
  List,
  ExternalLink,
  ChevronDown
} from 'lucide-react';

export interface Museo {
  id: number;
  nombre: string;
  universidad: string;
  naturaleza: 'Pública' | 'Privada' | 'No especificada';
  departamento: string;
  ciudad: string;
  direccion: string | null;
  tipologia: string | null;
  estadoAtencion: EstadoAtencion;
  registroSimco: 'Sí' | 'No' | 'En proceso / Por confirmar' | 'Sin información';
  paginaWeb: string | null;
  correoInstitucional: string | null;
}

export type EstadoAtencion = 'Abierto' | 'Cita previa' | 'Cerrado temporalmente' | 'Cerrado' | 'Sin información';

const ESTADO_BADGE: Record<EstadoAtencion, { className: string; label: string; short: string; dot?: string }> = {
  Abierto: { className: 'badge-open', label: 'Abierto', short: 'Abierto', dot: 'bg-emerald-500' },
  'Cita previa': { className: 'badge-appointment', label: 'Cita previa', short: 'Cita previa' },
  'Cerrado temporalmente': { className: 'badge-closed', label: 'Cierre temporal', short: 'Cierre temp.' },
  Cerrado: { className: 'badge-closed', label: 'Cerrado', short: 'Cerrado' },
  'Sin información': { className: 'badge-unknown', label: 'Sin información', short: 'Sin info.' },
};

const EstadoBadge: React.FC<{ estado: EstadoAtencion; compact?: boolean }> = ({ estado, compact = false }) => {
  const cfg = ESTADO_BADGE[estado];
  return (
    <span className={cfg.className}>
      {!compact && cfg.dot && <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`}></span>}
      {!compact && estado === 'Cita previa' && <Clock className="w-3 h-3" />}
      {compact ? cfg.short : cfg.label}
    </span>
  );
};

interface DirectorioMuseosProps {
  initialMuseos: Museo[];
}

export const DirectorioMuseos: React.FC<DirectorioMuseosProps> = ({ initialMuseos }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState<string>('TODOS');
  const [selectedNaturaleza, setSelectedNaturaleza] = useState<string>('TODAS');
  const [selectedEstado, setSelectedEstado] = useState<string>('TODOS');
  const [selectedSimco, setSelectedSimco] = useState<string>('TODOS');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  // Departamentos únicos con conteo
  const departamentosList = useMemo(() => {
    const counts: Record<string, number> = {};
    initialMuseos.forEach((m) => {
      counts[m.departamento] = (counts[m.departamento] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [initialMuseos]);

  // Filtrado reactivo
  const filteredMuseos = useMemo(() => {
    return initialMuseos.filter((museo) => {
      // Búsqueda textual
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase().trim();
        const matchesNombre = museo.nombre.toLowerCase().includes(query);
        const matchesUniv = museo.universidad.toLowerCase().includes(query);
        const matchesCiudad = museo.ciudad.toLowerCase().includes(query);
        const matchesTipologia = (museo.tipologia ?? '').toLowerCase().includes(query);
        if (!matchesNombre && !matchesUniv && !matchesCiudad && !matchesTipologia) {
          return false;
        }
      }

      // Filtro departamento
      if (selectedDept !== 'TODOS' && museo.departamento !== selectedDept) {
        return false;
      }

      // Filtro naturaleza
      if (selectedNaturaleza !== 'TODAS' && museo.naturaleza !== selectedNaturaleza) {
        return false;
      }

      // Filtro estado
      if (selectedEstado !== 'TODOS' && museo.estadoAtencion !== selectedEstado) {
        return false;
      }

      // Filtro SIMCO
      if (selectedSimco !== 'TODOS') {
        if (selectedSimco === 'REGISTRADO' && museo.registroSimco !== 'Sí') return false;
        if (selectedSimco === 'EN_PROCESO' && museo.registroSimco !== 'En proceso / Por confirmar') return false;
        if (selectedSimco === 'NO' && museo.registroSimco !== 'No') return false;
        if (selectedSimco === 'SIN_INFO' && museo.registroSimco !== 'Sin información') return false;
      }

      return true;
    });
  }, [initialMuseos, searchTerm, selectedDept, selectedNaturaleza, selectedEstado, selectedSimco]);

  // Reset page when filters change
  React.useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedDept, selectedNaturaleza, selectedEstado, selectedSimco]);

  const totalPages = Math.ceil(filteredMuseos.length / itemsPerPage);
  const paginatedMuseos = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredMuseos.slice(start, start + itemsPerPage);
  }, [filteredMuseos, currentPage]);

  const hasActiveFilters =
    searchTerm.trim() !== '' ||
    selectedDept !== 'TODOS' ||
    selectedNaturaleza !== 'TODAS' ||
    selectedEstado !== 'TODOS' ||
    selectedSimco !== 'TODOS';

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedDept('TODOS');
    setSelectedNaturaleza('TODAS');
    setSelectedEstado('TODOS');
    setSelectedSimco('TODOS');
    setCurrentPage(1);
  };

  return (
    <div className="space-y-8">
      {/* Search & Filter Toolbar */}
      <div className="bg-white rounded-2xl p-6 border border-gray-200/80 shadow-sm space-y-6">
        <div className="flex flex-col lg:flex-row gap-4 justify-between items-center">
          {/* Main Search Input */}
          <div className="relative w-full lg:w-96">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por museo, universidad, ciudad o tipología..."
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-gray-300 text-sm focus:border-brand-burgundy-700 focus:ring-1 focus:ring-brand-burgundy-700 bg-gray-50/50 hover:bg-white transition-colors"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                aria-label="Limpiar búsqueda"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* View Toggles & Clear */}
          <div className="flex items-center gap-3 w-full lg:w-auto justify-between lg:justify-end">
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-burgundy-700 hover:text-brand-burgundy-900 bg-brand-burgundy-50 hover:bg-brand-burgundy-100 px-3 py-2 rounded-lg transition-colors"
              >
                <X className="w-3.5 h-3.5" />
                Limpiar filtros
              </button>
            )}

            <div className="flex items-center rounded-xl bg-gray-100 p-1 border border-gray-200">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-lg text-sm transition-all ${
                  viewMode === 'grid'
                    ? 'bg-white text-brand-burgundy-900 shadow-sm font-semibold'
                    : 'text-gray-500 hover:text-gray-800'
                }`}
                title="Vista en cuadrícula"
                aria-label="Vista en cuadrícula"
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded-lg text-sm transition-all ${
                  viewMode === 'table'
                    ? 'bg-white text-brand-burgundy-900 shadow-sm font-semibold'
                    : 'text-gray-500 hover:text-gray-800'
                }`}
                title="Vista en tabla"
                aria-label="Vista en tabla"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Multifaceted Select Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-100">
          {/* Departamento */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Departamento
            </label>
            <div className="relative">
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                className="w-full appearance-none bg-gray-50 border border-gray-300 rounded-xl px-3.5 py-2 text-sm text-gray-800 focus:border-brand-burgundy-700 focus:ring-1 focus:ring-brand-burgundy-700 pr-8 cursor-pointer"
              >
                <option value="TODOS">Todos los departamentos ({initialMuseos.length})</option>
                {departamentosList.map(([dept, count]) => (
                  <option key={dept} value={dept}>
                    {dept} ({count})
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* Naturaleza */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Naturaleza Jurídica
            </label>
            <div className="relative">
              <select
                value={selectedNaturaleza}
                onChange={(e) => setSelectedNaturaleza(e.target.value)}
                className="w-full appearance-none bg-gray-50 border border-gray-300 rounded-xl px-3.5 py-2 text-sm text-gray-800 focus:border-brand-burgundy-700 focus:ring-1 focus:ring-brand-burgundy-700 pr-8 cursor-pointer"
              >
                <option value="TODAS">Todas las naturalezas</option>
                <option value="Pública">Universidad Pública</option>
                <option value="Privada">Universidad Privada</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* Estado de Atención */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Atención al Público
            </label>
            <div className="relative">
              <select
                value={selectedEstado}
                onChange={(e) => setSelectedEstado(e.target.value)}
                className="w-full appearance-none bg-gray-50 border border-gray-300 rounded-xl px-3.5 py-2 text-sm text-gray-800 focus:border-brand-burgundy-700 focus:ring-1 focus:ring-brand-burgundy-700 pr-8 cursor-pointer"
              >
                <option value="TODOS">Todos los estados</option>
                <option value="Abierto">Abierto</option>
                <option value="Cita previa">Con cita previa o programación</option>
                <option value="Cerrado temporalmente">Cerrado temporalmente</option>
                <option value="Cerrado">Cerrado</option>
                <option value="Sin información">Sin información</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* SIMCO */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Registro SIMCO
            </label>
            <div className="relative">
              <select
                value={selectedSimco}
                onChange={(e) => setSelectedSimco(e.target.value)}
                className="w-full appearance-none bg-gray-50 border border-gray-300 rounded-xl px-3.5 py-2 text-sm text-gray-800 focus:border-brand-burgundy-700 focus:ring-1 focus:ring-brand-burgundy-700 pr-8 cursor-pointer"
              >
                <option value="TODOS">Todos los registros</option>
                <option value="REGISTRADO">Inscrito en SIMCO (Sí)</option>
                <option value="EN_PROCESO">En proceso / Por confirmar</option>
                <option value="NO">No registrado</option>
                <option value="SIN_INFO">Sin información</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>
      </div>

      {/* Results Header Summary */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-1">
        <p className="text-sm text-gray-600">
          Mostrando <span className="font-bold text-gray-900">{filteredMuseos.length}</span> museos universitarios
          {hasActiveFilters && <span> que coinciden con los filtros aplicados</span>}
        </p>
        <span className="text-xs text-gray-500 bg-white px-3 py-1 rounded-full border border-gray-200">
          Base Consolidada RNMU 2026
        </span>
      </div>

      {/* Zero State */}
      {filteredMuseos.length === 0 && (
        <div className="text-center py-16 bg-white rounded-3xl border border-gray-200 p-8 space-y-4">
          <div className="w-16 h-16 mx-auto rounded-full bg-brand-burgundy-50 flex items-center justify-center text-brand-burgundy-800">
            <Filter className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-serif font-bold text-gray-900">No se encontraron museos con esos criterios</h3>
          <p className="text-sm text-gray-500 max-w-md mx-auto">
            Intenta cambiar los términos de búsqueda o restablecer los filtros para ver todos los museos de la Red.
          </p>
          <button
            onClick={clearFilters}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-burgundy-800 text-white text-sm font-medium hover:bg-brand-burgundy-900 transition-colors shadow-sm"
          >
            Ver todos los museos ({initialMuseos.length})
          </button>
        </div>
      )}

      {/* Grid View */}
      {viewMode === 'grid' && filteredMuseos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {paginatedMuseos.map((museo) => (
            <div
              key={museo.id}
              className="bg-white rounded-2xl border border-gray-200/80 p-6 flex flex-col justify-between hover:shadow-md hover:border-brand-burgundy-200 transition-all duration-200 group"
            >
              <div className="space-y-4">
                {/* Badges bar */}
                <div className="flex flex-wrap items-center gap-1.5">
                  <span
                    className={
                      museo.naturaleza === 'Pública' ? 'badge-pub' : 'badge-priv'
                    }
                  >
                    {museo.naturaleza}
                  </span>

                  <EstadoBadge estado={museo.estadoAtencion} />

                  {museo.registroSimco === 'Sí' && (
                    <span className="badge-simco" title="Registrado en el Sistema de Información de Museos Colombianos">
                      SIMCO ✓
                    </span>
                  )}
                </div>

                {/* Museum Title & University */}
                <div>
                  <h3 className="text-base font-serif font-bold text-gray-900 group-hover:text-brand-burgundy-800 transition-colors leading-snug">
                    {museo.nombre}
                  </h3>
                  <p className="text-xs font-semibold text-brand-navy-700 flex items-center gap-1.5 mt-1.5">
                    <Building2 className="w-3.5 h-3.5 shrink-0 text-brand-navy-500" />
                    <span>{museo.universidad}</span>
                  </p>
                </div>

                {/* Location */}
                <div className="flex items-start gap-1.5 text-xs text-gray-600 bg-gray-50/80 rounded-xl p-2.5 border border-gray-100">
                  <MapPin className="w-3.5 h-3.5 text-brand-burgundy-700 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-gray-800">{museo.ciudad}</span>
                    <span className="text-gray-500">, {museo.departamento}</span>
                    {museo.direccion && (
                      <p className="text-[11px] text-gray-500 mt-0.5 line-clamp-1">{museo.direccion}</p>
                    )}
                  </div>
                </div>

                {/* Typology */}
                <div className="text-xs text-gray-600">
                  <span className="font-semibold text-gray-700">Colección:</span>{' '}
                  <span className="text-gray-600 line-clamp-2">{museo.tipologia ?? 'Sin información'}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 mt-4 border-t border-gray-100 flex items-center gap-2">
                {museo.paginaWeb ? (
                  <a
                    href={museo.paginaWeb}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-brand-burgundy-800 bg-brand-burgundy-50 hover:bg-brand-burgundy-100 transition-colors"
                  >
                    <Globe className="w-3.5 h-3.5" />
                    Sitio Oficial
                    <ExternalLink className="w-3 h-3 text-brand-burgundy-500" />
                  </a>
                ) : (
                  <span className="flex-1 text-center py-2 text-xs text-gray-400 bg-gray-50 rounded-xl">
                    Sin web externa
                  </span>
                )}

                {museo.correoInstitucional && (
                  <a
                    href={`mailto:${museo.correoInstitucional}`}
                    className="p-2 rounded-xl text-gray-600 hover:text-brand-burgundy-800 bg-gray-50 hover:bg-brand-burgundy-50 transition-colors border border-gray-200"
                    title={`Contactar a ${museo.correoInstitucional}`}
                    aria-label={`Enviar correo a ${museo.correoInstitucional}`}
                  >
                    <Mail className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Table View */}
      {viewMode === 'table' && filteredMuseos.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-700">
              <thead className="bg-gray-50/80 text-[11px] uppercase tracking-wider text-gray-500 border-b border-gray-200">
                <tr>
                  <th scope="col" className="px-5 py-3 font-semibold">Museo / Espacio Cultural</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Universidad</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Ubicación</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Naturaleza</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Atención</th>
                  <th scope="col" className="px-4 py-3 font-semibold">SIMCO</th>
                  <th scope="col" className="px-4 py-3 font-semibold text-right">Contacto</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {paginatedMuseos.map((museo) => (
                  <tr key={museo.id} className="hover:bg-gray-50/60 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-serif font-bold text-gray-900 text-sm">{museo.nombre}</div>
                      <div className="text-gray-500 line-clamp-1">{museo.tipologia ?? 'Sin información'}</div>
                    </td>
                    <td className="px-4 py-3.5 font-medium text-gray-800">{museo.universidad}</td>
                    <td className="px-4 py-3.5">
                      <span className="font-semibold text-gray-800">{museo.ciudad}</span>, {museo.departamento}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={museo.naturaleza === 'Pública' ? 'badge-pub' : 'badge-priv'}>
                        {museo.naturaleza}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <EstadoBadge estado={museo.estadoAtencion} compact />
                    </td>
                    <td className="px-4 py-3.5">
                      {museo.registroSimco === 'Sí' ? (
                        <span className="text-emerald-700 font-medium">Registrado ✓</span>
                      ) : (
                        <span className="text-gray-400">{museo.registroSimco}</span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-right space-x-2">
                      {museo.paginaWeb && (
                        <a
                          href={museo.paginaWeb}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex p-1.5 rounded-lg text-brand-burgundy-700 hover:bg-brand-burgundy-50"
                          title="Visitar sitio web"
                        >
                          <Globe className="w-4 h-4" />
                        </a>
                      )}
                      {museo.correoInstitucional && (
                        <a
                          href={`mailto:${museo.correoInstitucional}`}
                          className="inline-flex p-1.5 rounded-lg text-gray-600 hover:bg-gray-100"
                          title={`Escribir a ${museo.correoInstitucional}`}
                        >
                          <Mail className="w-4 h-4" />
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Página <span className="font-semibold text-gray-800">{currentPage}</span> de{' '}
            <span className="font-semibold text-gray-800">{totalPages}</span>
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="px-3.5 py-1.5 rounded-xl border border-gray-300 text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Anterior
            </button>
            <div className="flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                // Show first, last, and window around current
                if (
                  page === 1 ||
                  page === totalPages ||
                  (page >= currentPage - 1 && page <= currentPage + 1)
                ) {
                  return (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={`w-8 h-8 rounded-xl text-xs font-semibold transition-all ${
                        currentPage === page
                          ? 'bg-brand-burgundy-800 text-white shadow-sm'
                          : 'text-gray-600 hover:bg-gray-100 bg-white border border-gray-200'
                      }`}
                    >
                      {page}
                    </button>
                  );
                }
                if (page === currentPage - 2 || page === currentPage + 2) {
                  return (
                    <span key={page} className="px-1 text-gray-400 text-xs">
                      ...
                    </span>
                  );
                }
                return null;
              })}
            </div>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3.5 py-1.5 rounded-xl border border-gray-300 text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
