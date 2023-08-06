"""The models file"""
from django.db import models

from django.apps import apps


class GOStatus(models.Model):
    """GeneralObjStatuses of the object are supported by generalobj.
    Even multiple times per object."""
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)
    parent_obj_description = models.CharField(max_length=128) #'$appname___$modelname
    next_statuses = models.CharField(max_length=256, blank=True, null=True, \
            default='')
    is_entrant = models.BooleanField(default=False)
    is_leaving = models.BooleanField(default=False)
    is_forward = models.BooleanField(default=True)
    is_backward = models.BooleanField(default=False)

    def get_next_statuses(self):
        """To get the next available status(es)"""
        return GOStatus.objects.filter(\
                parent_obj_description=self.parent_obj_description).filter(\
                code__in=self.next_statuses.split('|'))

    def add_status(self, name):
        """To add a next status to the current status"""
        if not self.next_statuses:
            self.next_statuses = ''
        if '|%s|' % name in self.next_statuses:
            return True
        else:
            if not self.next_statuses.startswith('|'):
                self.next_statuses = '|%s' % self.next_statuses
            if not self.next_statuses.endswith('|'):
                self.next_statuses += '|'
            self.next_statuses += '%s|' % name
            self.save()

    def remove_status(self, name):
        """To remove a status from the current status"""
        if '|%s|' % name in self.next_statuses:
            self.next_statuses = self.next_statuses.replace('%s|' % name, '')
            self.save()

    def add_statuses(self, name_lst):
        """To add more next_statuses to the current status"""
        self.next_statuses = '|%s|' % '|'.join(sorted(name_lst))
        self.save()


    def get_model(self):
        """To get the current model"""
        try:
            pob = self.parent_obj_description.split('___')
            model_base = apps.get_model(pob[0], pob[1])
            return model_base
        except:
            return False

    def get_attr_parts(self):
        """To get the attributes"""
        mdl = self.get_model()
        if mdl:
            try:
                pob = self.parent_obj_description.split('___')
                return (mdl, pob[2])
            except:
                return (mdl, 'status')
        else:
            return False

    def set_status(self, status):
        """Set the status of the current status"""
        self.status = status
        self.save()


    def change_parent_obj_status(self, parent_obj_id, ns_code, check_next_statuses=True):
        """Change the status of the related object"""
        if check_next_statuses:
            if not '|%s|' % ns_code in self.next_statuses:
                print("Status can't be set. %s is not next." % ns_code)
        ns_obj = GOStatus.objects.get(code=ns_code, \
                parent_obj_description=self.parent_obj_description)
        parent_obj_base, attr_name = self.get_attr_parts()
        parent_obj = parent_obj_base.objects.get(id=parent_obj_id)
        if parent_obj:
            setattr(parent_obj, attr_name, ns_obj)
            parent_obj.save()


    def __str__(self):
        """Str, display"""
        return '%s -> %s' % (self.code, self.next_statuses)
