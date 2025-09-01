import React, {useState, useEffect, useRef} from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  Appbar,
  TextInput,
  IconButton,
  Card,
  Text,
  Chip,
  ActivityIndicator,
  Snackbar,
} from 'react-native-paper';
import {SafeAreaView} from 'react-native-safe-area-context';
import {apiService, ChatResponse} from '../services/api';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  sources?: Array<{
    content: string;
    metadata: any;
    similarity: number;
  }>;
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [snackbar, setSnackbar] = useState({visible: false, message: ''});
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: '1',
        text: '🕳️ Welcome to Yak Hole! I can help you search through your personal notes and answer questions about them. What would you like to know?',
        isUser: false,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response: ChatResponse = await apiService.sendMessage({
        message: userMessage.text,
        conversation_id: conversationId,
      });

      setConversationId(response.conversation_id);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        isUser: false,
        timestamp: new Date(),
        sources: response.sources,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setSnackbar({
        visible: true,
        message: 'Failed to send message. Make sure the backend is running.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    Alert.alert(
      'Clear Chat',
      'Are you sure you want to clear the current conversation?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => {
            setMessages([
              {
                id: '1',
                text: '🕳️ Chat cleared. What would you like to know about your notes?',
                isUser: false,
                timestamp: new Date(),
              },
            ]);
            setConversationId(undefined);
          },
        },
      ],
    );
  };

  const renderMessage = ({item}: {item: Message}) => (
    <View
      style={[
        styles.messageContainer,
        item.isUser ? styles.userMessage : styles.botMessage,
      ]}>
      <Card
        style={[
          styles.messageCard,
          item.isUser ? styles.userCard : styles.botCard,
        ]}>
        <Card.Content>
          <Text
            style={[
              styles.messageText,
              item.isUser ? styles.userText : styles.botText,
            ]}>
            {item.text}
          </Text>
          {item.sources && item.sources.length > 0 && (
            <View style={styles.sourcesContainer}>
              <Text style={styles.sourcesTitle}>Sources:</Text>
              {item.sources.map((source, index) => (
                <Chip
                  key={index}
                  style={styles.sourceChip}
                  textStyle={styles.sourceChipText}
                  mode="outlined">
                  {source.metadata.filename || 'Unknown'} ({Math.round(source.similarity * 100)}%)
                </Chip>
              ))}
            </View>
          )}
        </Card.Content>
      </Card>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Yak Hole" subtitle="Your personal note assistant" />
        <Appbar.Action icon="delete" onPress={clearChat} />
      </Appbar.Header>

      <KeyboardAvoidingView
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          style={styles.messagesList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
          showsVerticalScrollIndicator={false}
        />

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Ask about your notes..."
            multiline
            maxLength={1000}
            disabled={isLoading}
            right={
              <TextInput.Icon
                icon={isLoading ? () => <ActivityIndicator size="small" /> : 'send'}
                onPress={sendMessage}
                disabled={isLoading || !inputText.trim()}
              />
            }
            onSubmitEditing={sendMessage}
          />
        </View>
      </KeyboardAvoidingView>

      <Snackbar
        visible={snackbar.visible}
        onDismiss={() => setSnackbar({visible: false, message: ''})}
        duration={3000}>
        {snackbar.message}
      </Snackbar>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardAvoid: {
    flex: 1,
  },
  messagesList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  messageContainer: {
    marginVertical: 4,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
  },
  botMessage: {
    alignSelf: 'flex-start',
  },
  messageCard: {
    elevation: 2,
  },
  userCard: {
    backgroundColor: '#6B4E3D',
  },
  botCard: {
    backgroundColor: '#ffffff',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: '#ffffff',
  },
  botText: {
    color: '#000000',
  },
  sourcesContainer: {
    marginTop: 8,
  },
  sourcesTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 4,
    color: '#666',
  },
  sourceChip: {
    marginRight: 4,
    marginBottom: 4,
  },
  sourceChipText: {
    fontSize: 10,
  },
  inputContainer: {
    padding: 16,
    backgroundColor: '#ffffff',
    elevation: 8,
  },
  textInput: {
    backgroundColor: '#f8f8f8',
  },
});