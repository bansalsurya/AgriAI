// src/screens/Home.tsx

import React, { useEffect, useState } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import WeatherAnalysis from './WeatherAnalysis';
import CropRecommendations from './CropRecommendations';
import YieldPredictor from './YieldPredictor';
import LocationHeader from '../components/LocationHeader'; // Import the LocationHeader
import { View } from 'react-native';

const Tab = createBottomTabNavigator();


const Home: React.FC<{ route: any }> = ({ route }) => {
  const { address, recommendations, advisory } = route.params;
  const [recc, setRecc] = useState()
  
  useEffect(()=>{
    setRecc(recommendations)
  },[route])

  return (
    <View style={{ flex: 1 }}>
      <LocationHeader address={address} />
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Weather Analysis') {
            iconName = focused ? 'weather-sunny' : 'weather-sunny-outline';
          } else if (route.name === 'Crop Recommendations') {
            iconName = focused ? 'seed-outline' : 'seed';
          } else if (route.name === 'Yield Predictor') {
            iconName = focused ? 'chart-bar' : 'chart-bar-outline';
          }

          return <MaterialCommunityIcons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#bc4749',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen 
        name="Weather Analysis" 
        children={() => <WeatherAnalysis advisory={advisory} />} 
      />
      <Tab.Screen 
        name="Crop Recommendations" 
      >
       {() => <CropRecommendations recommendations={recc} />}
      </Tab.Screen>
      <Tab.Screen 
        name="Yield Predictor" 
        children={() => <YieldPredictor address={address} />} 
      />
    </Tab.Navigator>
    </View>
  );
};

export default Home;
