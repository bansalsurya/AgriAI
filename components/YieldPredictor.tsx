import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet, Alert, TouchableOpacity, Text, FlatList } from 'react-native';
import RNHTMLtoPDF from 'react-native-html-to-pdf';
import MaterialIcons from 'react-native-vector-icons/MaterialIcons';
import yieldData from '../constants/yieldData.json'; // Import the JSON file

interface CropInput {
  cropName: string;
  acres: number;
}

const YieldPredictor: React.FC = () => {
  const [crops, setCrops] = useState<CropInput[]>([{ cropName: '', acres: 1 }]);
  const [results, setResults] = useState<any[]>([]);
  const [totalIncome, setTotalIncome] = useState(0);

  const handleAddRow = () => {
    if (crops.length < 5) {
      setCrops([...crops, { cropName: '', acres: 1 }]);
    } else {
      Alert.alert('Limit Reached', 'You can only add up to 5 crops.');
    }
  };

  const handleRemoveRow = (index: number) => {
    const updatedCrops = crops.filter((_, i) => i !== index);
    setCrops(updatedCrops);
  };

  const handleInputChange = (index: number, field: string, value: string) => {
    const updatedCrops = [...crops];
    if (field === 'cropName') {
      updatedCrops[index].cropName = value;
    } else if (field === 'acres') {
      updatedCrops[index].acres = parseInt(value) || 1;
    }
    setCrops(updatedCrops);
  };

  const calculateYield = () => {
    const yieldDataProcessed = crops.map((crop, index) => {
      // Use sample data for yield calculation
      const sampleData = yieldData[index % yieldData.length]; // Loop through sample data
      
      const expectedYield = sampleData.yieldPerAcre * crop.acres;
      const totalIncome = expectedYield * sampleData.pricePerKg;

      return {
        crop: crop.cropName || sampleData.crop,
        acres: crop.acres,
        yieldPerAcre: sampleData.yieldPerAcre,
        expectedYield,
        pricePerKg: sampleData.pricePerKg,
        totalIncome,
      };
    });

    setResults(yieldDataProcessed);
    setTotalIncome(yieldDataProcessed.reduce((sum, crop) => sum + crop.totalIncome, 0));
  };

  const downloadPDF = async () => {
    const html = `
      <h1>Yield Report</h1>
      <table style="width: 100%; border-collapse: collapse;">
        <tr>
          <th style="border: 1px solid black; padding: 8px;">Crop</th>
          <th style="border: 1px solid black; padding: 8px;">Acres</th>
          <th style="border: 1px solid black; padding: 8px;">Yield per Acre (kg)</th>
          <th style="border: 1px solid black; padding: 8px;">Expected Yield (kg)</th>
          <th style="border: 1px solid black; padding: 8px;">Price per kg ($)</th>
          <th style="border: 1px solid black; padding: 8px;">Total Income ($)</th>
        </tr>
        ${results.map(item => `
          <tr>
            <td style="border: 1px solid black; padding: 8px;">${item.crop}</td>
            <td style="border: 1px solid black; padding: 8px;">${item.acres}</td>
            <td style="border: 1px solid black; padding: 8px;">${item.yieldPerAcre}</td>
            <td style="border: 1px solid black; padding: 8px;">${item.expectedYield}</td>
            <td style="border: 1px solid black; padding: 8px;">${item.pricePerKg}</td>
            <td style="border: 1px solid black; padding: 8px;">${item.totalIncome}</td>
          </tr>
        `).join('')}
      </table>
      <h2>Total Income: $${totalIncome}</h2>
    `;

    const pdfOptions = {
      html,
      fileName: 'YieldReport',
      directory: 'Documents',
    };

    try {
      const file = await RNHTMLtoPDF.convert(pdfOptions);
      Alert.alert('PDF Created', `Your PDF is saved at: ${file.filePath}`);
    } catch (error) {
      Alert.alert('Error', 'Failed to create PDF');
    }
  };

  return (
    <View style={styles.container}>
      {crops.map((crop, index) => (
        <View key={index} style={styles.row}>
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Crop</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter Crop Name"
              value={crop.cropName}
              onChangeText={(text) => handleInputChange(index, 'cropName', text)}
            />
          </View>
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Acres</Text>
            <TextInput
              style={styles.acresInput}
              placeholder="1"
              keyboardType="numeric"
              value={crop.acres.toString()}
              onChangeText={(text) => handleInputChange(index, 'acres', text)}
            />
          </View>
          <TouchableOpacity onPress={() => handleRemoveRow(index)} style={styles.removeButton}>
            <Text style={styles.removeButtonText}>Remove</Text>
          </TouchableOpacity>
        </View>
      ))}

      {crops.length < 5 && (
        <TouchableOpacity style={styles.addButton} onPress={handleAddRow}>
          <Text style={styles.addButtonText}>+ Add Crop</Text>
        </TouchableOpacity>
      )}

      <TouchableOpacity style={styles.calculateButton} onPress={calculateYield}>
        <Text style={styles.coinIcon}>💰</Text>
        <Text style={styles.calculateButtonText}>Calculate Yield</Text>
      </TouchableOpacity>

      {results.length > 0 && (
        <View style={styles.resultsContainer}>
        <Text style={styles.resultsTitle}>Yield Results</Text>
        <View style={styles.resultsHeader}>
          <Text style={styles.headerText}>Crop</Text>
          <Text style={styles.headerText}>Acres</Text>
          <Text style={styles.headerText}>Yield/Acre</Text>
          <Text style={styles.headerText}>Expected Yield</Text>
          <Text style={styles.headerText}>Price/Kg</Text>
          <Text style={styles.headerText}>Total Income</Text>
        </View>
        <FlatList
          data={results}
          keyExtractor={(item) => item.crop}
          renderItem={({ item }) => (
            <View style={styles.resultRow}>
              <Text style={styles.resultText}>{item.crop}</Text>
              <Text style={styles.resultText}>{item.acres.toFixed(2)}</Text>
              <Text style={styles.resultText}>{`${item.yieldPerAcre.toFixed(2)} Kg/Acre`}</Text>
              <Text style={styles.resultText}>{`${item.expectedYield.toFixed(2)} Kg`}</Text>
              <Text style={styles.resultText}>{`Rs. ${item.pricePerKg.toFixed(2)}`}</Text>
              <Text style={styles.resultText}>{`Rs. ${item.totalIncome.toFixed(2)}`}</Text>
            </View>
          )}
        />
            <TouchableOpacity style={styles.downloadButton} onPress={downloadPDF}>
                <View style={styles.downloadButtonContent}>
                    <MaterialIcons name="download" size={20} color="white" />
                    <Text style={styles.downloadButtonText}>Download</Text>
                </View>
            </TouchableOpacity>
      </View>
      )}
    </View>
  );
};


const styles = StyleSheet.create({
    container: {
      padding: 20,
      backgroundColor: '#f5f5f5',
    },
    row: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 15,
    },
    inputContainer: {
      flex: 2,
      marginRight: 10,
    },
    label: {
      fontSize: 12,
      color: '#333',
      marginBottom: 3,
    },
    input: {
      height: 40,
      borderColor: '#ccc',
      borderWidth: 1,
      borderRadius: 5,
      paddingHorizontal: 10,
    },
    acresInput: {
      height: 40,
      borderColor: '#ccc',
      borderWidth: 1,
      borderRadius: 5,
      paddingHorizontal: 10,
      textAlign: 'center',
    },
    removeButton: {
      backgroundColor: '#ff4d4d',
      paddingHorizontal: 10,
      paddingVertical: 5,
      borderRadius: 5,
    },
    removeButtonText: {
      color: 'white',
      fontWeight: 'bold',
    },
    addButton: {
      alignSelf: 'flex-start',
      backgroundColor: '#4CAF50',
      paddingHorizontal: 15,
      paddingVertical: 8,
      borderRadius: 5,
      marginBottom: 20,
      marginTop: 10,
    },
    addButtonText: {
      color: 'white',
      fontWeight: 'bold',
    },
    calculateButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#ff8c00',
      paddingVertical: 12,
      borderRadius: 5,
      marginTop: 20,
    },
    coinIcon: {
      marginRight: 8,
      fontSize: 20,
    },
    calculateButtonText: {
      color: 'white',
      fontWeight: 'bold',
    },
    resultsContainer: {
      marginTop: 20,
      backgroundColor: '#fff',
      borderRadius: 5,
      padding: 10,
      elevation: 3, // Shadow effect for Android
      shadowColor: '#000', // Shadow effect for iOS
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 2,
    },
    resultsTitle: {
      fontSize: 18,
      fontWeight: 'bold',
      marginBottom: 10,
    },
    resultRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      paddingVertical: 5,
      borderBottomWidth: 1,
      borderBottomColor: '#ccc',
    },
    resultText: {
      flex: 1,
      textAlign: 'left',
      paddingHorizontal: 5,
    },
    resultsHeader: {
        flexDirection: 'row',
        backgroundColor: '#eee',
        paddingVertical: 10,
        paddingHorizontal: 5,
        borderRadius: 5,
      },
      headerText: {
        flex: 1,
        fontWeight: 'bold',
        textAlign: 'center',
        borderBottomWidth: 1,
        borderBottomColor: '#ccc',
        color: '#333',
      },
      downloadButton: {
        backgroundColor: '#007BFF',
        padding: 10,
        borderRadius: 5,
        alignItems: 'center',
        marginTop: 10,
    },
    downloadButtonContent: {
        flexDirection: 'row', // Align icon and text in a row
        alignItems: 'center', // Center vertically
    },
    downloadButtonText: {
        color: 'white',
        fontWeight: 'bold',
        marginLeft: 5, // Space between icon and text
    },
  });
  
export default YieldPredictor;
