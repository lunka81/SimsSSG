import "./PersonTable.css";
import PersonDetails from "./PersonDetails";
import { Search, Funnel, ChevronDown, ArrowUp, ArrowDown, ChevronsUpDown, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

// Beskriver hur en person ser ut. export så att Admin kan använda den
export type Person = {
    id: string;
    name: string;
    access: string;
    department: string;
};

type PersonTableProps = {
    //array av personer som ska visas i tabellen
    persons: Person[];
    onDelete: (id: string) => Promise<void>;
};

type SortKey = "name" | "access" | "department";
type SortDirection = "asc" | "desc";

// Antal personer per sida
const PAGE_SIZE = 10;

function PersonTable({ persons, onDelete }: PersonTableProps) {
    const [search, setSearch] = useState("");
    const [permission, setPermission] = useState("all");
    const [department, setDepartment] = useState("all");
    const [sortKey, setSortKey] = useState<SortKey | null>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
    const [page, setPage] = useState(1);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const selectedPerson = persons.find((person) => person.id === selectedId);

    // Hämtar alla avdelningar som finns bland personerna, utan dubbletter och tomma värden
    const departments = [...new Set(persons.map((person) => person.department))]
        .filter((name) => name !== "")
        .sort();

    const filteredPersons = persons.filter((person) => {
        // Söker bara på namn
        const matchesSearch = person.name.toLowerCase().includes(search.toLowerCase());

        const matchesPermission =
            permission === "all" || person.access === permission;

        const matchesDepartment =
            department === "all" || person.department === department;

        return matchesSearch && matchesPermission && matchesDepartment;
    });

    // Sorterar de filtrerade personerna. [...] gör en kopia så att originallistan inte ändras.
    // Ingen vald kolumn: personerna visas i den ordning backend skickar dem (sorterade på namn)
    const sortedPersons = sortKey === null
        ? filteredPersons
        : [...filteredPersons].sort((a, b) => {
            const result = a[sortKey].localeCompare(b[sortKey], "sv");
            return sortDirection === "asc" ? result : -result;
        });

    // Räknar ut hur många sidor det blir och vilka personer som syns på aktuell sida
    const totalPages = Math.max(1, Math.ceil(sortedPersons.length / PAGE_SIZE));
    const currentPage = Math.min(page, totalPages);
    const start = (currentPage - 1) * PAGE_SIZE;
    const visiblePersons = sortedPersons.slice(start, start + PAGE_SIZE);

    // Klick på samma rubrik vänder ordningen, klick på en ny rubrik sorterar stigande
    function handleSort(key: SortKey) {
        if (key === sortKey) {
            setSortDirection(sortDirection === "asc" ? "desc" : "asc");
        } else {
            setSortKey(key);
            setSortDirection("asc");
        }
        setPage(1);
    }

    // Visar vilken kolumn som är sorterad och åt vilket håll
    function sortIcon(key: SortKey) {
        if (key !== sortKey) return <ChevronsUpDown size={14} />;
        return sortDirection === "asc" ? <ArrowUp size={14} /> : <ArrowDown size={14} />;
    }

    // Återställer sökning, filter och sortering
    function clearFilters() {
        setSearch("");
        setPermission("all");
        setDepartment("all");
        setSortKey(null);
        setSortDirection("asc");
        setPage(1);
    }

    return (
        <section className="person-table">
            <div className="person-table-toolbar">
                <label className="person-table-search">
                    <Search size={18} />
                    <input
                        type="text"
                        placeholder="Search by name..."
                        value={search}
                        onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                    />
                </label>

                {/*Varje filter är en ruta med en liten rubrik ovanför valet*/}
                <label className="person-table-filter">
                    <span>Permission</span>
                    <select value={permission} onChange={(e) => { setPermission(e.target.value); setPage(1); }}>
                        <option value="all">All</option>
                        <option value="Standard">Standard</option>
                        <option value="Admin">Admin</option>
                        <option value="Limited">Limited</option>
                    </select>
                    <ChevronDown size={16} className="filter-arrow" />
                </label>

                <label className="person-table-filter">
                    <span>Department</span>
                    <select value={department} onChange={(e) => { setDepartment(e.target.value); setPage(1); }}>
                        <option value="all">All</option>
                        {departments.map((name) => (
                            <option key={name} value={name}>{name}</option>
                        ))}
                    </select>
                    <ChevronDown size={16} className="filter-arrow" />
                </label>

                <button type="button" className="person-table-clear" onClick={clearFilters}>
                    <Funnel size={16} />
                    Clear filters
                </button>
            </div>
            <div className="person-table-card">
                <h2>{filteredPersons.length} of {persons.length} persons</h2>

                <div className="person-table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                {/*Kolumnrubriker. Klick sorterar på kolumnen*/}
                                <th>
                                    <button type="button" className="sort-button" onClick={() => handleSort("name")}>
                                        Name {sortIcon("name")}
                                    </button>
                                </th>
                                <th>
                                    <button type="button" className="sort-button" onClick={() => handleSort("access")}>
                                        Permission {sortIcon("access")}
                                    </button>
                                </th>
                                <th>
                                    <button type="button" className="sort-button" onClick={() => handleSort("department")}>
                                        Department {sortIcon("department")}
                                    </button>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {/*Går igenom alla personer i arrayen och skapar en tabellrad för varje person*/}
                            {visiblePersons.map((person) => (
                                <tr key={person.id} className="person-row" onClick={() => setSelectedId(person.id)}>
                                    <td>{person.name}</td>
                                    <td>{person.access}</td>
                                    <td>{person.department}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {/*Knappar för att bläddra mellan sidorna*/}
                <div className="person-table-pagination">
                    <span>
                        Showing {sortedPersons.length === 0 ? 0 : start + 1}–{start + visiblePersons.length} of {sortedPersons.length}
                    </span>

                    <div className="pagination-buttons">
                        <button
                            type="button"
                            className="icon-button"
                            title="Previous page"
                            disabled={currentPage === 1}
                            onClick={() => setPage(currentPage - 1)}
                        >
                            <ChevronLeft size={16} />
                        </button>

                        <span>Page {currentPage} of {totalPages}</span>

                        <button
                            type="button"
                            className="icon-button"
                            title="Next page"
                            disabled={currentPage === totalPages}
                            onClick={() => setPage(currentPage + 1)}
                        >
                            <ChevronRight size={16} />
                        </button>
                    </div>
                </div>
            </div>
            {/*Popup med detaljer om den valda personen*/}
            {selectedPerson && (
                <PersonDetails
                    person={selectedPerson}
                    onClose={() => setSelectedId(null)}
                    onDelete={onDelete}
                />
            )}
        </section>
    );
}

export default PersonTable;
