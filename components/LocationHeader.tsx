// src/components/LocationHeader.tsx

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const LocationHeader: React.FC<{ address: { country: string; state: string; area: string } }> = ({ address }) => {
  return (
    <View style={styles.headerContainer}>
      <Text style={styles.headerText}>Location: {address.area}, {address.state}, {address.country}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  headerContainer: {
    backgroundColor: '#6a994e', // Match your app background color
    padding: 10,
    alignItems: 'center',
  },
  headerText: {
    fontSize: 18,
    color: 'white',
  },
});

export default LocationHeader;
