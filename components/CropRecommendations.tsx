import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import recommendationsData from '../constants/recommendation.json';

interface CropRecommendation {
  crop: string;
  type: string;
  score: string;
  reason: string;
}

interface CropRecommendationsProps {
  recommendations: CropRecommendation[];
}

const getScoreColor = (score: number) => {
  if (score >= 75) return 'green';
  if (score >= 50) return 'orange';
  return 'red';
};

const CropRecommendations: React.FC<CropRecommendationsProps> = ({ recommendations }) => {
  const [rec, setRecommendations] = useState<CropRecommendation[]>([]);

  useEffect(() => {
    setRecommendations(recommendations.length ? recommendations : recommendationsData);
  }, [recommendations]);

  return (
    <View style={styles.container}>
      <FlatList
        data={rec}
        keyExtractor={(item) => item.crop}
        renderItem={({ item }) => {
          const scoreValue = parseInt(item.score.replace('SCORE: ', ''));
          return (
            <View style={styles.cropContainer}>
              <Text style={styles.cropText}>{item.crop}</Text>
              <Text style={styles.cropDetail}>{item.type}</Text>
              <Text style={[styles.cropScore, { color: getScoreColor(scoreValue) }]}>{item.score}</Text>
              <Text style={styles.cropReason}>{item.reason}</Text>
            </View>
          );
        }}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f0f0f0',
  },
  cropContainer: {
    marginBottom: 15,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.3,
    shadowRadius: 2,
    elevation: 4,
    borderLeftWidth: 5,
    borderLeftColor: '#4CAF50', // green border for visual appeal
  },
  cropText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  cropDetail: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  cropScore: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 6,
  },
  cropReason: {
    marginTop: 8,
    fontSize: 12,
    color: '#777',
    lineHeight: 18,
  },
});

export default CropRecommendations;
