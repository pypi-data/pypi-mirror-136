from django.contrib import admin

from openlxp_notifications.models import ReceiverEmailConfiguration, \
    SenderEmailConfiguration, \
    EmailConfiguration


@admin.register(ReceiverEmailConfiguration)
class ReceiverEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('email_address',)


@admin.register(SenderEmailConfiguration)
class SenderEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('sender_email_address',)


# @admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('Subject',
                    'Signature',
                    'Email_Us',
                    'FAQ_URL',
                    'Unsubscribe_Email_ID',
                    'Content_Type',
                    'Email_Content',
                    'HTML_File',
                    )
    fieldsets = (('Email Configuration', {'fields': ('Subject',
                                                     'Signature',
                                                     'Email_Us',
                                                     'FAQ_URL',
                                                     'Unsubscribe_Email_ID',
                                                     'Content_Type',
                                                     'Email_Content',
                                                     'HTML_File',),
                                          'classes': ('class1',)
                                          }),
                 )

    class Media:
        js = ('category-field-admin.js',)


admin.site.register(EmailConfiguration, EmailConfigurationAdmin)
