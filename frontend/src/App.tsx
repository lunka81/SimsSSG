import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home/Home";
import AdminLayout from "./pages/Admin/AdminLayout";
import Admin from "./pages/Admin/Admin";
import Persons from "./pages/Admin/components/Persons";

/*Roten i appen: bestämmer vilken sida som visas för vilken adress*/
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Admin />} />
          <Route path="persons" element={<Persons />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
