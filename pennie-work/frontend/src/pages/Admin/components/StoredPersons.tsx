import "./StoredPersons.css";
import { Pencil, Trash2 } from "lucide-react";
import { useState } from "react";
import { employeeImageUrl } from "../../../api";

// Beskriver hur en person ser ut. export så att Admin kan använda den
export type Person = {
    // uuid från databasen
    id: string;
    name: string;
    access: string;
    department: string;
    active: boolean;
};

type StoredPersonsProps = {
    //array av personer som ska visas i tabellen
    persons: Person[];
    onDelete: (id: string) => void;
    // Anropas när man klickar på en rad i tabellen
    onSelect: (id: string) => void;
};

function StoredPersons({ persons, onDelete, onSelect }: StoredPersonsProps) {
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
                            <th>Picture</th>
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
                            <tr key={person.id} className="clickable-row" onClick={() => onSelect(person.id)}>
                                <td><img className="person-picture" src={employeeImageUrl(person.id)} alt="" /></td>
                                <td>{person.name}</td>
                                <td>{person.access}</td>
                                <td>{person.department}</td>
                                {/*Om personen är aktive===true, returnera Active, annars returnera Inactive*/}
                                <td>{person.active ? "Active" : "Inactive"}</td>
                                <td>
                                    {/*Klick på knapparna ska inte också öppna personens detaljer*/}
                                    <div className="action-buttons" onClick={(e) => e.stopPropagation()}>
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