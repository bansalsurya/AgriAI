import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';

interface WarningCardProps {
    climateType: string;
    risks: string[];
    scheduleNotification: any;
}

const WarningCard: React.FC<WarningCardProps> = ({ climateType, risks, scheduleNotification }) => {
    const animationValue = useRef(new Animated.Value(0)).current;
    useEffect(()=>{
        scheduleNotification("High temperature alert! Stay hydrated.")
    })
    // Function to handle the flashing effect
    const startFlashing = () => {
        Animated.loop(
            Animated.sequence([
                Animated.timing(animationValue, {
                    toValue: 1,
                    duration: 500, // Duration for the flash
                    useNativeDriver: false,
                }),
                Animated.timing(animationValue, {
                    toValue: 0,
                    duration: 500,
                    useNativeDriver: false,
                }),
            ])
        ).start();
    };

    useEffect(() => {
        startFlashing();
    }, []);

    // Interpolating the animation value to change the opacity
    const opacity = animationValue.interpolate({
        inputRange: [0, 1],
        outputRange: [0.5, 1], // Flashing effect
    });

    return (
        <View style={styles.card}>
            <Text style={styles.climateType}>Climate Type: {climateType}</Text>
            <Text style={styles.risksTitle}>⚠️ Environmental Risks:</Text>
            {risks.map((risk, index) => (
                <View key={index} style={styles.riskItemContainer}>
                    <Animated.View style={[styles.flashingCircle, { opacity }]} />
                    <Text style={styles.riskItem}>{risk}</Text>
                </View>
            ))}
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff5b0', // Light yellow background
        padding: 15,
        borderRadius: 8,
        marginBottom: 20,
        borderWidth: 2,
        borderColor: '#ffcc00',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.2,
        shadowRadius: 1,
        elevation: 3,
    },
    climateType: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    risksTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: 5,
    },
    riskItemContainer: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    flashingCircle: {
        width: 10,
        height: 10,
        borderRadius: 5,
        backgroundColor: '#fe7f2d', // Red circle color
        marginRight: 5,
    },
    riskItem: {
        fontSize: 14,
        color: '#333',
    },
});

export default WarningCard;
