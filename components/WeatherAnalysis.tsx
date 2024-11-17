import React, { useEffect, useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import WarningCard from './WarningCard'; // Adjust the import path as necessary
import environmentalRisksData from '../constants/risk.json'; // Adjust the import path
import ForecastCard from './ForcastCard';
import SoilSummaryCard from './SoilInformationCard';
import soilData from '../constants/soilData.json';
import ManagementRequirementsCard from './ManagamentRequirementCard';
import * as Notifications from 'expo-notifications';
import * as Permissions from 'expo-permissions';

const WeatherAnalysis: React.FC = (advisory: any) => {
    const [climateType, setClimateType] = useState<string>('');
    const [risks, setRisks] = useState<string[]>([]);
    useEffect(() => {
        registerForPushNotificationsAsync();
      }, []);
    
      const registerForPushNotificationsAsync = async () => {
        const { status: existingStatus } = await Permissions.getAsync(Permissions.NOTIFICATIONS);
        let finalStatus = existingStatus;
    
        if (existingStatus !== 'granted') {
          const { status } = await Permissions.askAsync(Permissions.NOTIFICATIONS);
          finalStatus = status;
        }
    
        if (finalStatus !== 'granted') {
          alert('Failed to get push token for push notification!');
          return;
        }
    
        // Get the token for sending notifications
        const token = await Notifications.getExpoPushTokenAsync();
        console.log(token); // Send this token to your backend to store it if needed
      };

    const scheduleNotification = async (alertMessage) => {
        await Notifications.scheduleNotificationAsync({
          content: {
            title: "Weather Alert!",
            body: alertMessage,
            data: { someData: 'goes here' },
          },
          trigger: { seconds: 1 }, // This can be adjusted based on when you want to trigger the alert
        });
    };
    
    useEffect(() => {
        setClimateType(environmentalRisksData.climate_type);
        setRisks(environmentalRisksData.risks);
    }, []);
    return (
        <View style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollView}>
                <WarningCard climateType={climateType} risks={risks} scheduleNotification={scheduleNotification} advisory={advisory?.advisory?.environmental_conditions} />
                <ForecastCard weatherAnalysis={advisory?.advisory?.weather_analysis} />
                <SoilSummaryCard data={soilData} advisory={advisory?.advisory?.soil_analysis}/>
                <ManagementRequirementsCard requirements={soilData?.detailed_characteristics?.fertility_indicators?.management_requirements} advisory={advisory?.advisory?.soil_analysis?.detailed_characteristics?.fertility_indicators?.management_requirements}/>
            </ScrollView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    scrollView: {
        paddingBottom: 20, // Optional: Add some padding to the bottom
    },
});

export default WeatherAnalysis;
