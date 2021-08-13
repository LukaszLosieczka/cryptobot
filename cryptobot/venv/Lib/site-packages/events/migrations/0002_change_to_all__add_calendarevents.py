# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Renaming model 'EventsPlugin'
        db.rename_table('cmsplugin_eventsplugin', 'events_alleventsplugin')

        # Execute update of plugins in cms_cmsplugin
        db.execute("UPDATE cms_cmsplugin SET plugin_type = %s WHERE plugin_type = %s", ["AllEventsPlugin", "EventsPlugin"])

        # Change number_to_show max_length
        db.alter_column('events_alleventsplugin', 'number_to_show', self.gf('django.db.models.fields.IntegerField')(max_length=4))

        # Adding model 'CalendarEventsPlugin'
        db.create_table('events_calendareventsplugin', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(primary_key=True, unique=True, to=orm['cms.CMSPlugin'])),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Calendar'])),
            ('number_to_show', self.gf('django.db.models.fields.IntegerField')(max_length=4)),
        ))
        db.send_create_signal('events', ['CalendarEventsPlugin'])


    def backwards(self, orm):
        # Renaming model 'AllEventsPlugin' back
        db.rename_table('events_alleventsplugin', 'cmsplugin_eventsplugin')

        # Execute update of plugins in cms_cmsplugin
        db.execute("UPDATE cms_cmsplugin SET plugin_type = %s WHERE plugin_type = %s", ["EventsPlugin", "AllEventsPlugin"])

        # Change number_to_show max_length
        # Discarded due to the previous version using choices that made this unecessary.
        # No reason to alter the field when the scenario this would protect is not possible.
        # db.alter_column('cmsplugin_alleventsplugin', 'number_to_show', self.gf('django.db.models.fields.IntegerField')(max_length=10))

        # Deleting model 'CalendarEventsPlugin'
        db.delete_table('events_calendareventsplugin')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['cms.CMSPlugin']", 'null': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'blank': 'True', 'null': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'events.alleventsplugin': {
            'Meta': {'object_name': 'AllEventsPlugin', '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'number_to_show': ('django.db.models.fields.IntegerField', [], {'max_length': '4'})
        },
        'events.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'unique': 'True'})
        },
        'events.calendareventsplugin': {
            'Meta': {'object_name': 'CalendarEventsPlugin', '_ormbases': ['cms.CMSPlugin']},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Calendar']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'number_to_show': ('django.db.models.fields.IntegerField', [], {'max_length': '4'})
        },
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'audience': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Calendar']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['resources.Person']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['resources.Organization']", 'null': 'True'}),
            'max_size': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'unique': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'})
        },
        'resources.organization': {
            'Meta': {'object_name': 'Organization'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['resources.Organization']", 'null': 'True', 'related_name': "'children'"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'unique': 'True'})
        },
        'resources.person': {
            'Meta': {'object_name': 'Person'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_first': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name_last': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['resources.Organization']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True', 'null': 'True'})
        }
    }

    complete_apps = ['events']
