import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home/Home";
import AdminLayout from "./pages/Admin/AdminLayout";
import Admin from "./pages/Admin/Admin";
import Persons from "./pages/Admin/components/Persons";
import Logbook from "./pages/Admin/components/Logbook";

/**
 * The root of the app. Decides which page is shown for which address.
 *
 * "/" is the access view. The pages under "/admin" share the same layout
 * and can only be opened by a logged-in admin.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Admin />} />
          <Route path="persons" element={<Persons />} />
          <Route path="logbook" element={<Logbook />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
