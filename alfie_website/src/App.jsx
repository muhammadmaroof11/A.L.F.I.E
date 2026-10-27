import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LawFirmsPage from './pages/LawFirmsPage';
import ClinicsPage from './pages/ClinicsPage';
import RealEstatePage from './pages/RealEstatePage';
import CarRentalPage from './pages/CarRentalPage';
import HospitalityPage from './pages/HospitalityPage';

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

export default function App() {
  return (
    <Router>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/law-firms" element={<LawFirmsPage />} />
        <Route path="/clinics" element={<ClinicsPage />} />
        <Route path="/real-estate" element={<RealEstatePage />} />
        <Route path="/car-rental" element={<CarRentalPage />} />
        <Route path="/hospitality" element={<HospitalityPage />} />
      </Routes>
    </Router>
  );
}
