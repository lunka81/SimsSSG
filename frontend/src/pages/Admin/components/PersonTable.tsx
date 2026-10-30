import "./PersonTable.css";
import PersonDetails from "./PersonDetails";
import { Search, Funnel, ChevronDown, ArrowUp, ArrowDown, ChevronsUpDown, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

/** A person as it is shown in the admin interface. */
export type Person = {
    id: string;
    name: string;
    permission: string;
    department: string;
};

type PersonTableProps = {
    /** The persons to show in the table. */
    persons: Person[];
    onDelete: (id: string) => Promise<void>;
};

type SortKey = "name" | "permission" | "department";
type SortDirection = "asc" | "desc";

// Number of persons per page
const PAGE_SIZE = 10;

/**
 * Table of persons with search, filters, sorting and pages.
 * A click on a row opens a popup with details about the person.
 */
function PersonTable({ persons, onDelete }: PersonTableProps) {
    const [search, setSearch] = useState("");
    const [permissionFilter, setPermissionFilter] = useState("all");
    const [departmentFilter, setDepartmentFilter] = useState("all");
    const [sortKey, setSortKey] = useState<SortKey | null>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
    const [page, setPage] = useState(1);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const selectedPerson = persons.find((person) => person.id === selectedId);

    // Collects all departments among the persons, without duplicates and empty values
    const departments = [...new Set(persons.map((person) => person.department))]
        .filter((name) => name !== "")
        .sort();

    const filteredPersons = persons.filter((person) => {
        // Searches by name only
        const matchesSearch = person.name.toLowerCase().includes(search.toLowerCase());

        const matchesPermission =
            permissionFilter === "all" || person.permission === permissionFilter;

        const matchesDepartment =
            departmentFilter === "all" || person.department === departmentFilter;

        return matchesSearch && matchesPermission && matchesDepartment;
    });

    // Sorts the filtered persons. [...] makes a copy so that the original list is not changed.
    // No chosen column: the persons are shown in the order the backend sends them (sorted by name)
    const sortedPersons = sortKey === null
        ? filteredPersons
        : [...filteredPersons].sort((a, b) => {
            const result = a[sortKey].localeCompare(b[sortKey], "sv");
            return sortDirection === "asc" ? result : -result;
        });

    // Calculates the number of pages and which persons are shown on the current page
    const totalPages = Math.max(1, Math.ceil(sortedPersons.length / PAGE_SIZE));
    const currentPage = Math.min(page, totalPages);
    const start = (currentPage - 1) * PAGE_SIZE;
    const visiblePersons = sortedPersons.slice(start, start + PAGE_SIZE);

    // A click on the same heading reverses the order, a click on a new heading sorts ascending
    function handleSort(key: SortKey) {
        if (key === sortKey) {
            setSortDirection(sortDirection === "asc" ? "desc" : "asc");
        } else {
            setSortKey(key);
            setSortDirection("asc");
        }
        setPage(1);
    }

    // Shows which column is sorted and in which direction
    function sortIcon(key: SortKey) {
        if (key !== sortKey) return <ChevronsUpDown size={14} />;
        return sortDirection === "asc" ? <ArrowUp size={14} /> : <ArrowDown size={14} />;
    }

    // Resets the search, filters and sorting
    function clearFilters() {
        setSearch("");
        setPermissionFilter("all");
        setDepartmentFilter("all");
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

                {/* Each filter is a box with a small heading above the choice */}
                <label className="person-table-filter">
                    <span>Permission</span>
                    <select value={permissionFilter} onChange={(e) => { setPermissionFilter(e.target.value); setPage(1); }}>
                        <option value="all">All</option>
                        <option value="Standard">Standard</option>
                        <option value="Admin">Admin</option>
                        <option value="Limited">Limited</option>
                    </select>
                    <ChevronDown size={16} className="filter-arrow" />
                </label>

                <label className="person-table-filter">
                    <span>Department</span>
                    <select value={departmentFilter} onChange={(e) => { setDepartmentFilter(e.target.value); setPage(1); }}>
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
                                {/* Column headings. A click sorts by the column */}
                                <th>
                                    <button type="button" className="sort-button" onClick={() => handleSort("name")}>
                                        Name {sortIcon("name")}
                                    </button>
                                </th>
                                <th>
                                    <button type="button" className="sort-button" onClick={() => handleSort("permission")}>
                                        Permission {sortIcon("permission")}
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
                            {/* Creates one table row for each person on the current page */}
                            {visiblePersons.map((person) => (
                                <tr key={person.id} className="person-row" onClick={() => setSelectedId(person.id)}>
                                    <td>{person.name}</td>
                                    <td>{person.permission}</td>
                                    <td>{person.department}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {/* Buttons for moving between the pages */}
                <div className="person-table-pagination">
                    <span>
                        Showing {sortedPersons.length === 0 ? 0 : start + 1}-{start + visiblePersons.length} of {sortedPersons.length}
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
            {/* Popup with details about the chosen person */}
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