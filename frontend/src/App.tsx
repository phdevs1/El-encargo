import { BrowserRouter, Route, Routes } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { HostQueuePage } from "./pages/HostQueuePage";
import { JoinPage } from "./pages/JoinPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { StatusPage } from "./pages/StatusPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/l/:slug" element={<JoinPage />} />
        <Route path="/l/:slug/status/:token" element={<StatusPage />} />
        <Route path="/host/:locationId" element={<HostQueuePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
