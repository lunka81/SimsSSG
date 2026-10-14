import "./StoredPersons.css";
import { Pencil, Trash2 } from "lucide-react";
import { useState } from "react";

// Beskriver hur en person ser ut. export så att Admin kan använda den
export type Person = {
    id: number;
    name: string;
    access: string;
    department: string;
    active: boolean;
};

type StoredPersonsProps = {
    //array av personer som ska visas i tabellen
    persons: Person[];
    onDelete: (id: number) => void;
};

function StoredPersons({ persons, onDelete }: StoredPersonsProps) {
    const [search, setSearch] = useState("");
    const [permission, setPermission] = useState("all");

    const filteredPersons = persons.filter((person) => {
        const matchesSearch =
            person.name.toLowerCase().includes(search.toLowerCase()) ||
            person.access.toLowerCase().includes(search.toLowerCase()) ||
            person.department.toLowerCase().includes(search.toLowerCase()) ||
            (search.toLowerCase() === "active" && person.active === true) ||
            (search.toLowerCase() === "inactive" && person.active === false);

        const matchesPermission =
            permission === "all" || person.access === permission;

        return matchesSearch && matchesPermission;
    });

    function handleDelete(person: Person) {
        if (window.confirm(`Do you want to remove ${person.name}?`)) {
            onDelete(person.id);
        }
    }
    return (
        <section className="stored-persons">
            <h2>Stored persons</h2>

            <div className="stored-toolbar">
                <input type="text" placeholder="Search by name or status..." value={search} onChange={(e) => setSearch(e.target.value)} />
                <select value={permission} onChange={(event) => setPermission(event.target.value)}>
                    <option value="all">All permissions</option>
                    <option value="Standard">Standard</option>
                    <option value="Admin">Admin</option>
                    <option value="Limited">Limited</option>
                </select>
            </div>

            <div className="table-wrapper">
                <table className="stored-table">
                    <thead>
                        <tr>
                            {/*Kolumnrubriker för tabellen*/}
                            <th>Name</th>
                            <th>Permission</th>
                            <th>Description</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {/*Går igenom alla personer i arrayen och skapar en tabellrad för varje person*/}
                        {filteredPersons.map((person) => (
                            <tr key={person.id}>
                                <td>{person.name}</td>
                                <td>{person.access}</td>
                                <td>{person.department}</td>
                                {/*Om personen är aktive===true, returnera Active, annars returnera Inactive*/}
                                <td>{person.active ? "Active" : "Inactive"}</td>
                                <td>
                                    <div className="action-buttons">
                                        <button type="button" className="icon-button" title="Edit">
                                            <Pencil size={16} />
                                        </button>
                                        <button type="button" className="icon-button" title="Remove" onClick={() => handleDelete(person)}>
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
}

export default StoredPersons;