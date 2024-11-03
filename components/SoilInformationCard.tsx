import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

interface SoilSummaryCardProps {
  soilData: {
    composition: {
      primary_type: string;
      texture: string;
      particle_size: string;
      structure: string;
      color: string;
    };
    physical: {
      bulk_density: string;
      porosity: string;
      compaction: string;
      organic_matter_content: string;
    };
    chemical: {
      ph: {
        classification: string;
      };
      salt_content: {
        level: string;
      };
    };
    fertility: {
      fertility_level: string;
      nutrient_availability: {
        nitrogen: string;
        phosphorus: string;
        potassium: string;
        micronutrients: string;
      };
      management_requirements: string[];
    };
  };
}

const getColorAndIcon = (value) => {
    let iconName;
    let iconColor;
  
    if (value === 'High') {
      iconName = 'alert-circle';
      iconColor = 'red';
    } else if (value === 'Low') {
      iconName = 'alert';
      iconColor = 'orange';
    } else {
      iconName = 'check-circle';
      iconColor = 'green';
    }
  
    return { name: iconName, color: iconColor };
};

const SoilSummaryCard: React.FC<SoilSummaryCardProps> = ({ soilData }) => {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>Soil Summary</Text>

      <View style={styles.row}>
        <Text style={styles.label}>Primary Type:</Text>
        <Text style={styles.value}>{soilData.composition.primary_type}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Texture:</Text>
        <Text style={styles.value}>{soilData.composition.texture}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Bulk Density:</Text>
        <Text style={styles.value}>
          {soilData.physical.bulk_density} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.physical.bulk_density).name}
            color={getColorAndIcon(soilData.physical.bulk_density).color}
            size={18}
            />
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Porosity:</Text>
        <Text style={styles.value}>
          {soilData.physical.porosity} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.physical.porosity).name}
            color={getColorAndIcon(soilData.physical.porosity).color}
            size={18}
            />
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Compaction:</Text>
        <Text style={styles.value}>
          {soilData.physical.compaction} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.physical.compaction).name}
            color={getColorAndIcon(soilData.physical.compaction).color}
            size={18}
            />
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Organic Matter Content:</Text>
        <Text style={styles.value}>
          {soilData.physical.organic_matter_content} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.physical.organic_matter_content).name}
            color={getColorAndIcon(soilData.physical.organic_matter_content).color}
            size={18}
            />
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>pH Level:</Text>
        <Text style={styles.value}>
          {soilData.chemical.ph.classification} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.chemical.ph.classification).name}
            color={getColorAndIcon(soilData.chemical.ph.classification).color}
            size={18}
            />
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Salt Content:</Text>
        <Text style={styles.value}>
          {soilData.chemical.salt_content.level} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.chemical.salt_content.level).name}
            color={getColorAndIcon(soilData.chemical.salt_content.level).color}
            size={18}
            />
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Fertility Level:</Text>
        <Text style={styles.value}>
          {soilData.fertility.fertility_level} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.fertility.fertility_level).name}
            color={getColorAndIcon(soilData.fertility.fertility_level).color}
            size={18}
            />
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Nutrient Availability:</Text>
        <Text style={styles.value}>
          {`N: ${soilData.fertility.nutrient_availability.nitrogen}`} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.fertility.nutrient_availability.nitrogen).name}
            color={getColorAndIcon(soilData.fertility.nutrient_availability.nitrogen).color}
            size={18}
            />
        </Text>
        <Text style={styles.value}>
          {`P: ${soilData.fertility.nutrient_availability.phosphorus}`} 
          <MaterialCommunityIcons
            name={getColorAndIcon(soilData.fertility.nutrient_availability.phosphorus).name}
            color={getColorAndIcon(soilData.fertility.nutrient_availability.phosphorus).color}
            size={18}
            />
        </Text>
        <Text style={styles.value}>
          {`K: ${soilData.fertility.nutrient_availability.potassium}`} 
           <MaterialCommunityIcons
            name={getColorAndIcon(soilData.fertility.nutrient_availability.potassium).name}
            color={getColorAndIcon(soilData.fertility.nutrient_availability.potassium).color}
            size={18}
            />
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginVertical: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 2.5,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  label: {
    fontWeight: '600',
    color: '#555',
  },
  requirementsList: {
    marginTop: 5,
    paddingLeft: 10,
  },
  requirementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  bullet: {
    color: '#333',
    fontSize: 18,
    marginRight: 5,
  },
  value: {
    color: '#333',
    flex: 1,
    textAlign: 'right',
  },
});

export default SoilSummaryCard;
