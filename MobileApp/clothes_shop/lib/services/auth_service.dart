import 'package:clothes_shop/services/api_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:clothes_shop/config/constants.dart';
import 'package:clothes_shop/models/user.dart';

class AuthService {
  final ApiService _apiService = ApiService();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  
  Future<Map<String, dynamic>> register({
    required String name,
    required String email,
    required String phone,
    required String password,
    required String passwordConfirm,
  }) async {
    try {
      final response = await _apiService.post('/auth/register/', data: {
        'name': name,
        'email': email,
        'phone': phone,
        'password': password,
        'password_confirm': passwordConfirm,
      });
      
      // Save tokens
      await _storage.write(key: AppConstants.tokenKey, value: response.data['access']);
      await _storage.write(key: AppConstants.refreshTokenKey, value: response.data['refresh']);
      
      return response.data;
    } catch (e) {
      throw Exception('Registration failed: ${e.toString()}');
    }
  }
  
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _apiService.post('/auth/login/', data: {
        'email': email,
        'password': password,
      });
      
      // Save tokens
      await _storage.write(key: AppConstants.tokenKey, value: response.data['access']);
      await _storage.write(key: AppConstants.refreshTokenKey, value: response.data['refresh']);
      
      return response.data;
    } catch (e) {
      throw Exception('Login failed: ${e.toString()}');
    }
  }
  
  Future<void> logout() async {
    try {
      final refreshToken = await _storage.read(key: AppConstants.refreshTokenKey);
      if (refreshToken != null) {
        await _apiService.post('/auth/logout/', data: {
          'refresh': refreshToken,
        });
      }
    } catch (e) {
      // Continue with logout even if API call fails
    } finally {
      await _storage.deleteAll();
    }
  }
  
  Future<bool> isAuthenticated() async {
    final token = await _storage.read(key: AppConstants.tokenKey);
    return token != null;
  }
  
  Future<User?> getCurrentUser() async {
    try {
      final response = await _apiService.get('/users/me/');
      return User.fromJson(response.data);
    } catch (e) {
      return null;
    }
  }
  
  Future<void> changePassword({
    required String oldPassword,
    required String newPassword,
  }) async {
    try {
      await _apiService.post('/auth/change-password/', data: {
        'old_password': oldPassword,
        'new_password': newPassword,
      });
    } catch (e) {
      throw Exception('Password change failed: ${e.toString()}');
    }
  }
  
  Future<void> resetPassword({required String email}) async {
    try {
      await _apiService.post('/auth/password-reset/', data: {
        'email': email,
      });
    } catch (e) {
      throw Exception('Password reset failed: ${e.toString()}');
    }
  }
}