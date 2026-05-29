import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/diagnosis_model.dart';
import '../../../data/repositories/diagnosis_repository.dart';

class ChatMessage {
  final String text;
  final bool isUser;
  final DiagnosisModel? diagnosis;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.diagnosis,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class ChatState {
  final List<ChatMessage> messages;
  final bool isLoading;

  const ChatState({this.messages = const [], this.isLoading = false});

  ChatState copyWith({List<ChatMessage>? messages, bool? isLoading}) {
    return ChatState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class ChatNotifier extends StateNotifier<ChatState> {
  final DiagnosisRepository _repo;

  ChatNotifier(this._repo) : super(const ChatState()) {
    _addWelcomeMessage();
  }

  void _addWelcomeMessage() {
    state = state.copyWith(messages: [
      ChatMessage(
        text: 'Halo! Saya AgriBrain AI, asisten agronomis digital Anda. Ceritakan masalah tanaman Anda dan saya akan membantu mendiagnosisnya.',
        isUser: false,
      ),
    ]);
  }

  Future<void> sendMessage(String query) async {
    final userMsg = ChatMessage(text: query, isUser: true);
    state = state.copyWith(messages: [...state.messages, userMsg], isLoading: true);

    try {
      final diagnosis = await _repo.askAgronomist(query: query);
      state = state.copyWith(
        messages: [
          ...state.messages,
          ChatMessage(
            text: diagnosis.diagnosis,
            isUser: false,
            diagnosis: diagnosis,
          ),
        ],
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        messages: [
          ...state.messages,
          ChatMessage(
            text: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
            isUser: false,
          ),
        ],
        isLoading: false,
      );
    }
  }
}

final chatProvider = StateNotifierProvider<ChatNotifier, ChatState>((ref) {
  return ChatNotifier(ref.read(diagnosisRepositoryProvider));
});
