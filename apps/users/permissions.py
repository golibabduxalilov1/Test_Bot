from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_teacher
        )


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_student
        )


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_teacher or request.user.is_admin)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True

        # Test egasi yoki o'quvchi o'z javobini ko'rishi mumkin
        if hasattr(obj, "teacher"):
            return obj.teacher == request.user
        if hasattr(obj, "student"):
            return obj.student == request.user

        return False
