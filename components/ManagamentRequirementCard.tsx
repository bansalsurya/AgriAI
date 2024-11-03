import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const ManagementRequirementsCard = ({ requirements }) => {
  return (
    <View style={styles.cardContainer}>
      <Text style={styles.title}>Soil Management Requirements</Text>
      <View style={styles.requirementsList}>
        {requirements.map((item, index) => (
          <View key={index} style={styles.requirementItem}>
            <MaterialCommunityIcons name="check-circle" color="#4CAF50" size={16} style={styles.icon} />
            <Text style={styles.requirementText}>{item}</Text>
          </View>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  cardContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginVertical: 10,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  requirementsList: {
    paddingLeft: 10,
  },
  requirementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 5,
  },
  icon: {
    marginRight: 10,
  },
  requirementText: {
    fontSize: 15,
    color: '#555',
  },
});

export default ManagementRequirementsCard;
