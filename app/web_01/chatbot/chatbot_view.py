from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .gemini_service import GeminiChatbot
from web_01.models import ChatHistory

@login_required
def chatbot_view(request):
    """Hiển thị giao diện chatbot"""
    # Lấy lịch sử chat gần đây
    recent_chats = ChatHistory.objects.all().order_by('-created_at')[:10]
    
    context = {
        'recent_chats': recent_chats
    }
    
    return render(request, 'apps/web_01/dashboard/chatbot.html', context)

@csrf_exempt
@login_required
def chatbot_api(request):
    """API endpoint cho chatbot"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            if not data and request.POST:
                # Xử lý form data
                user_message = request.POST.get('message', '')
            else:
                user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Không có tin nhắn'
                }, status=400)
            
            # Khởi tạo chatbot
            chatbot = GeminiChatbot()
            
            # Xử lý câu hỏi
            bot_reply = chatbot.process_query(user_message)
            
            # Lưu lịch sử chat
            chatbot.save_chat_history(user_message, bot_reply)
            
            return JsonResponse({
                'status': 'success',
                'reply': bot_reply
            })
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@login_required
def get_chat_history(request):
    """API endpoint để lấy lịch sử chat"""
    try:
        # Lấy 10 cuộc trò chuyện gần nhất
        chat_history = ChatHistory.objects.all().order_by('-created_at')[:10]
        
        # Đảo ngược để hiển thị theo thứ tự thời gian
        chat_history = reversed(list(chat_history))
        
        # Chuyển đổi thành JSON
        history_data = []
        for chat in chat_history:
            history_data.append({
                'user_message': chat.user_message,
                'bot_reply': chat.bot_reply,
                'created_at': chat.created_at.strftime('%d/%m/%Y %H:%M:%S')
            })
        
        return JsonResponse({
            'status': 'success',
            'chat_history': history_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
