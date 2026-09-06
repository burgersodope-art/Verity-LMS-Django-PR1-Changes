# >>> CHANGED in commit dd7a321 — This PR introduces comprehensive improvements to the Content Management System across both the Django Backend and React Frontend: (lines 1-28)
import os
import re

files = [
    r'd:\Verity-LMS-Django-prod-dev\Verity-LMS-Django-prod-dev\trial_lms_backend\content_management\views\student_views.py',
    r'd:\Verity-LMS-Django-prod-dev\Verity-LMS-Django-prod-dev\trial_lms_backend\content_management\views\teacher_views.py',
    r'd:\Verity-LMS-Django-prod-dev\Verity-LMS-Django-prod-dev\trial_lms_backend\content_management\views\admin_views.py',
    r'd:\Verity-LMS-Django-prod-dev\Verity-LMS-Django-prod-dev\trial_lms_backend\common\audit_mixins.py'
]

for file_path in files:
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix request arguments
    content = re.sub(r'request=request,', 'user=request.user,', content)
    content = re.sub(r'request=self\.request,', 'user=self.request.user,', content)
    
    # Fix module argument to object_type
    content = re.sub(r'module=\"', 'object_type="', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Successfully fixed audit_log parameters in backend views.")
