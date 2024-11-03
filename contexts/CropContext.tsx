import React, { createContext, useContext, useState } from 'react';

interface CropRecommendation {
  crop: string;
  type: string;
  score: string;
  reason: string;
}

interface CropContextType {
  recommendations: CropRecommendation[];
  setRecommendations: React.Dispatch<React.SetStateAction<CropRecommendation[]>>;
}

const CropContext = createContext<CropContextType | undefined>(undefined);

export const CropProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [recommendations, setRecommendations] = useState<CropRecommendation[]>([]);

  return (
    <CropContext.Provider value={{ recommendations, setRecommendations }}>
      {children}
    </CropContext.Provider>
  );
};

export const useCropContext = () => {
  const context = useContext(CropContext);
  if (!context) {
    throw new Error("useCropContext must be used within a CropProvider");
  }
  return context;
};
