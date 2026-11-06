import "./PersonTable.css";
import PersonDetails from "./PersonDetails";
import type { PersonDetailsUpdate } from "./PersonDetails";
import {
  PERMISSIONS,
  updateEmployee,
  type Employee,
  type Permission,
} from "../../../api/employees";
import {
  Search,
  Funnel,
  ChevronDown,
  ArrowUp,
  ArrowDown,
  ChevronsUpDown,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";

export type Person = {
  id: string;
  name: string;
  access: string;
  department: string;
};

type PersonTableProps = {
  persons: Person[];
  onDelete: (id: string) => Promise<void>;

  // Kan användas för att även uppdatera listan i Admin.
  onUpdated?: (person: Person) => void;
};

type SortKey = "name" | "access" | "department";
type SortDirection = "asc" | "desc";

const PAGE_SIZE = 10;

function toPerson(employee: Employee): Person {
  return {
    id: employee.uuid,
    name: employee.name,
    access: employee.permission,
    department: employee.description ?? "",
  };
}

function isPermission(value: string): value is Permission {
  return PERMISSIONS.some((permission) => permission === value);
}

function PersonTable({
  persons,
  onDelete,
  onUpdated,
}: PersonTableProps) {
  const [search, setSearch] = useState("");
  const [permission, setPermission] = useState("all");
  const [department, setDepartment] = useState("all");
  const [sortKey, setSortKey] = useState<SortKey | null>(null);
  const [sortDirection, setSortDirection] =
    useState<SortDirection>("asc");
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Visar sparade ändringar direkt även utan onUpdated från Admin.
  const [updatedPersons, setUpdatedPersons] =
    useState<Record<string, Person>>({});

  const currentPersons = persons.map(
    (person) => updatedPersons[person.id] ?? person
  );

  const selectedPerson = currentPersons.find(
    (person) => person.id === selectedId
  );

  const departments = [
    ...new Set(currentPersons.map((person) => person.department)),
  ]
    .filter((name) => name.trim() !== "")
    .sort();

  const filteredPersons = currentPersons.filter((person) => {
    const matchesSearch = person.name
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesPermission =
      permission === "all" || person.access === permission;

    const matchesDepartment =
      department === "all" || person.department === department;

    return matchesSearch && matchesPermission && matchesDepartment;
  });

  const sortedPersons =
    sortKey === null
      ? filteredPersons
      : [...filteredPersons].sort((a, b) => {
          const result = a[sortKey].localeCompare(b[sortKey], "sv");

          return sortDirection === "asc" ? result : -result;
        });

  const totalPages = Math.max(
    1,
    Math.ceil(sortedPersons.length / PAGE_SIZE)
  );

  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * PAGE_SIZE;
  const visiblePersons = sortedPersons.slice(
    start,
    start + PAGE_SIZE
  );

  function handleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDirection((current) =>
        current === "asc" ? "desc" : "asc"
      );
    } else {
      setSortKey(key);
      setSortDirection("asc");
    }

    setPage(1);
  }

  function sortIcon(key: SortKey) {
    if (key !== sortKey) {
      return <ChevronsUpDown size={14} />;
    }

    return sortDirection === "asc" ? (
      <ArrowUp size={14} />
    ) : (
      <ArrowDown size={14} />
    );
  }

  function clearFilters() {
    setSearch("");
    setPermission("all");
    setDepartment("all");
    setSortKey(null);
    setSortDirection("asc");
    setPage(1);
  }

  async function handleSavePerson(
    id: string,
    changes: PersonDetailsUpdate
  ): Promise<void> {
    if (!isPermission(changes.access)) {
      throw new Error("Select a valid permission.");
    }

    // Mappar formulärets fält till backendens schema.
    const employee = await updateEmployee(id, {
      name: changes.name,
      permission: changes.access,
      description: changes.department,
      ...(changes.image !== undefined
        ? { img: changes.image }
        : {}),
    });

    const updatedPerson = toPerson(employee);

    setUpdatedPersons((current) => ({
      ...current,
      [id]: updatedPerson,
    }));

    onUpdated?.(updatedPerson);

    // PersonDetails stänger dialogen efter lyckad sparning.
    // Om PATCH misslyckas kastas felet vidare till dialogen.
  }

  async function handleDeletePerson(id: string): Promise<void> {
    await onDelete(id);

    setUpdatedPersons((current) => {
      const next = { ...current };
      delete next[id];
      return next;
    });

    setSelectedId(null);
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
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
          />
        </label>

        <label className="person-table-filter">
          <span>Permission</span>

          <select
            value={permission}
            onChange={(event) => {
              setPermission(event.target.value);
              setPage(1);
            }}
          >
            <option value="all">All</option>

            {PERMISSIONS.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>

          <ChevronDown size={16} className="filter-arrow" />
        </label>

        <label className="person-table-filter">
          <span>Department</span>

          <select
            value={department}
            onChange={(event) => {
              setDepartment(event.target.value);
              setPage(1);
            }}
          >
            <option value="all">All</option>

            {departments.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>

          <ChevronDown size={16} className="filter-arrow" />
        </label>

        <button
          type="button"
          className="person-table-clear"
          onClick={clearFilters}
        >
          <Funnel size={16} />
          Clear filters
        </button>
      </div>

      <div className="person-table-card">
        <h2>
          {filteredPersons.length} of {currentPersons.length} persons
        </h2>

        <div className="person-table-wrapper">
          <table>
            <thead>
              <tr>
                <th>
                  <button
                    type="button"
                    className="sort-button"
                    onClick={() => handleSort("name")}
                  >
                    Name {sortIcon("name")}
                  </button>
                </th>

                <th>
                  <button
                    type="button"
                    className="sort-button"
                    onClick={() => handleSort("access")}
                  >
                    Permission {sortIcon("access")}
                  </button>
                </th>

                <th>
                  <button
                    type="button"
                    className="sort-button"
                    onClick={() => handleSort("department")}
                  >
                    Department {sortIcon("department")}
                  </button>
                </th>
              </tr>
            </thead>

            <tbody>
              {visiblePersons.map((person) => (
                <tr
                  key={person.id}
                  className="person-row"
                  onClick={() => setSelectedId(person.id)}
                >
                  <td>{person.name}</td>
                  <td>{person.access}</td>
                  <td>{person.department}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="person-table-pagination">
          <span>
            Showing {sortedPersons.length === 0 ? 0 : start + 1}–
            {start + visiblePersons.length} of {sortedPersons.length}
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

            <span>
              Page {currentPage} of {totalPages}
            </span>

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

      {selectedPerson && (
        <PersonDetails
          key={selectedPerson.id}
          person={selectedPerson}
          permissionOptions={PERMISSIONS}
          onClose={() => setSelectedId(null)}
          onDelete={handleDeletePerson}
          onSave={handleSavePerson}
        />
      )}
    </section>
  );
}

export default PersonTable;