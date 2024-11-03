import React, { useState } from 'react';
import { View, Text, Modal, StyleSheet, TextInput, TouchableOpacity,ActivityIndicator } from 'react-native';
import * as Location from 'expo-location';
import { Colors } from '../constants/colors';
import { MaterialCommunityIcons } from '@expo/vector-icons'; 
import axios from 'axios';

const Main: React.FC<any> = ({ navigation }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [country, setCountry] = useState<string>('');
  const [state, setState] = useState<string>('');
  const [area, setArea] = useState<string>('');
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);


  const openModal = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    
    if (status !== 'granted') {
      console.warn('Permission to access location was denied');
      return;
    }

    const locationResult = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Highest,
    });

    const { latitude, longitude } = locationResult.coords;
    const addressArray = await Location.reverseGeocodeAsync({ latitude, longitude });
    const address = addressArray[0];

    setCountry(address.country || '');
    setState(address.region || '');
    setArea(address.postalCode || '');
    setLatitude(latitude); 
    setLongitude(longitude); 
    setModalVisible(true);
  };

  const handleProceed = async () => {
    const latString = String(latitude); // Convert latitude to string
    const longString = String(longitude); // Convert longitude to string
    const addressString = String(area); // Convert area (postal code) to string
    
    setLoading(true);

    try {
        const response = await fetch('http://127.0.0.1:8000/recommend-crops/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lat: latString,
                long: longString,
                address: addressString,
            }),
        });
        const data = await response.json();
        console.log(data)
        setRecommendations(data);
        setModalVisible(false);
      
      // Navigate to the Home screen after setting the recommendations
      navigation.navigate("Home", {
        address: {
          country,
          state,
          area,
        },
        recommendations: recommendations
      });
      
    } catch (error) {
      console.error('Error fetching crop recommendations:', error);
      // Handle error appropriately, e.g., show a message to the user
    } finally {
        setLoading(false); // Set loading to false after the request completes
    }
  };

  const refreshLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    
    if (status !== 'granted') {
      console.warn('Permission to access location was denied');
      return;
    }

    const locationResult = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Highest,
    });

    const { latitude, longitude } = locationResult.coords;
    const addressArray = await Location.reverseGeocodeAsync({ latitude, longitude });
    const address = addressArray[0];

    setCountry(address.country || '');
    setState(address.region || '');
    setArea(address.postalCode || '');
  };

  return (
    <View style={styles.container}>
      <MaterialCommunityIcons name="leaf" size={24} color="white" style={styles.icon} />
      <Text style={styles.appName}>AgriAI</Text>
      <Text style={styles.appSubText}>Your one-stop farming solution</Text>
      <Text style={styles.appSubText}>powered by AI.</Text>

      <TouchableOpacity style={styles.proceedButton} onPress={openModal}>
        <Text style={styles.proceedButtonText}>Get Started</Text>
      </TouchableOpacity>

      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalText}>Please enter your location details:</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Country"
              value={country}
              onChangeText={setCountry}
            />
            <TextInput
              style={styles.input}
              placeholder="State"
              value={state}
              onChangeText={setState}
            />
            <TextInput
              style={styles.input}
              placeholder="Area / Postal Code"
              value={area}
              onChangeText={setArea}
            />

            <TouchableOpacity style={styles.selectLocationButton} onPress={refreshLocation}>
                <MaterialCommunityIcons name="map-marker" size={20} color="white" style={styles.iconlocation} />
                <Text style={styles.selectLocationButtonText}>Select Location</Text>
            </TouchableOpacity>
            {loading ? ( // Show loading spinner if loading is true
                <ActivityIndicator size="large" color="#0000ff" style={styles.loader} />
            ) : (
                <TouchableOpacity
                style={styles.proceedButton}
                onPress={handleProceed}
              >
                <Text style={styles.proceedButtonText}>Proceed</Text>
              </TouchableOpacity>
            )}

          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  loader: {
    marginTop: 20, // Adjust margin as needed
  },
  container: {
    flex: 1,
    backgroundColor: '#6a994e',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
    width: '80%',
  },
  modalText: {
    marginBottom: 15,
    fontSize: 18,
    textAlign: 'center',
  },
  input: {
    height: 40,
    borderColor: Colors.primaryGrey,
    borderWidth: 1,
    borderRadius: 5,
    width: '100%',
    paddingHorizontal: 10,
    marginVertical: 5,
  },
  selectLocationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4a7c59',
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 5,
    marginTop: 20,
  },
  selectLocationButtonText: {
    color: 'white',
    fontSize: 16,
  },
  proceedButton: {
    backgroundColor: '#bc4749',
    borderRadius: 5,
    paddingVertical: 10,
    paddingHorizontal: 20,
    marginTop: 40,
  },
  proceedButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 18,
  },
  icon: {
    marginLeft: 110,
  },
  iconlocation: {
    marginBottom: 5,
    marginRight: 5
  },
  appName: {
    fontSize: 36,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 20,
    textAlign: 'center',
  },
  appSubText: {
    fontSize: 13,
    color: 'white',
    textAlign: 'center',
  },
});

export default Main;
