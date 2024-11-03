import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import weatherData from '../constants/weatherData.json'; // Adjust the path as necessary

const ForecastCard: React.FC = () => {
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        // Simulate fetching data from JSON file
        setData(weatherData);
    }, []);

    if (!data) {
        return null; // You can return a loader here if necessary
    }

    return (
        <View style={styles.card}>
            <Text style={styles.header}>Weather Forecast</Text>

            <View style={styles.row}>
                <MaterialCommunityIcons name="weather-sunny" size={24} color="orange" />
                <Text style={styles.infoText}>
                    {data.temperature.value} {data.temperature.unit} ({data.temperature.classification})
                </Text>
            </View>

            <View style={styles.row}>
                <MaterialCommunityIcons name="water" size={24} color="blue" />
                <Text style={styles.infoText}>
                    {data.humidity.value} {data.humidity.unit} ({data.humidity.classification})
                </Text>
            </View>

            <View style={styles.row}>
                <MaterialCommunityIcons name="weather-solar" size={24} color="yellow" />
                <Text style={styles.infoText}>
                    {data.solar_radiation.value.toFixed(2)} {data.solar_radiation.unit} ({data.solar_radiation.classification})
                </Text>
            </View>

            <View style={styles.row}>
                <MaterialCommunityIcons name="weather-windy" size={24} color="grey" />
                <Text style={styles.infoText}>
                    {data.wind.speed} {data.wind.unit} - Dust Storm Probability: {data.wind.dust_storm_probability}
                </Text>
            </View>

            {data.environmental_risks.length > 0 && (
                <View style={styles.row}>
                    <MaterialCommunityIcons name="alert" size={24} color="red" />
                    <Text style={styles.infoText}>
                        Risks: {data.environmental_risks.join(', ')}
                    </Text>
                </View>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff',
        padding: 15,
        borderRadius: 8,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.2,
        shadowRadius: 1,
        elevation: 3,
    },
    header: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    row: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    infoText: {
        marginLeft: 10,
        fontSize: 16,
        color: '#333',
    },
});

export default ForecastCard;
