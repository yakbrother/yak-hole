import React from 'react';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {PaperProvider, MD3LightTheme} from 'react-native-paper';
import ChatScreen from './app/screens/ChatScreen';

const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#6B4E3D',
    secondary: '#8B7355',
  },
};

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <ChatScreen />
      </PaperProvider>
    </SafeAreaProvider>
  );
}