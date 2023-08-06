OBJECT_CREATE = {
    "apiVersion": "objects.mavq.io/v1",
    "kind": "Operation",
    "metadata": {
        "tenant": "admin"
    },
    "spec": {
        "manifest": {
            "objectConfigurationSpec": {
                "name": "pythonobject",
                "display": {
                    "singularLabel": "pythonobject",
                    "pluralLabel": "pythonobject",
                    "description": ""
                },
                "visibility": "public-read-write-delete",
                "storage": {
                    "mode": "RDBMS"
                }
            },
            "systemFields": {
                "nameFieldDisplay": {
                    "label": "name",
                    "description": "",
                    "helpText": "",
                    "placeholder": ""
                },
                "nameFieldUnique": True
            }
        },
        "options": {
            "retryLimit": 5
        },
        "type": "create_object"
    }
}

OBJECT_UPDATE = {
    "kind": "ObjectConfiguration",
    "apiVersion": "objects.mavq.io/v1",
    "metadata": {
        "system": {
            "controls": {
                "access": {
                    "readOnly": False,
                    "hidden": False,
                    "nonDeletable": False
                }
            },
            "hooks": [],
            "audit": {
                "createdAt": "2022-06-07T08:36:00.183Z",
                "updatedAt": "2022-06-07T08:36:06.405Z",
                "createdBy": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "updatedBy": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "versions": [],
                "operations": [],
                "owner": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "versionNumber": 1
            },
            "selfLink": "mavq:objects://tenants/admin/object_configurations/pythonobject"
        },
        "tenant": "admin",
        "uid": "pythonobject"
    },
    "spec": {
        "name": "pythonobject",
        "display": {
            "singularLabel": "pythonobjectUpdate",
            "pluralLabel": "pythonobjectUpdate",
            "description": ""
        },
        "visibility": "public-read-write-delete",
        "storage": {
            "mode": "RDBMS",
            "versioning": {
                "versionLimit": 2,
                "versionDays": 30
            }
        }
    }
}

FIELD_CREATE = {
    "kind": "ObjectField",
    "apiVersion": "objects.mavq.io/v1",
    "metadata": {
        "tenant": "admin"
    },
    "spec": {
        "objectConfigurationUri": "mavq:objects://tenants/admin/object_configurations/abcprojects",
        "display": {
            "description": "",
            "helpText": "",
            "label": "emailfield",
            "placeholder": ""
        },
        "definition": {
            "type": "EMAIL",
            "name": "emailfield",
            "mandatory": True,
            "indexing": False,
            "immutable": False,
            "unique": True,
            "allowedDomains": [
                "mavq.com"
            ]
        }
    }
}

FIELD_UPDATE = {
    "kind": "ObjectField",
    "apiVersion": "objects.mavq.io/v1",
    "metadata": {
        "system": {
            "controls": {
                "access": {
                    "readOnly": False,
                    "hidden": False,
                    "nonDeletable": False
                }
            },
            "hooks": [],
            "audit": {
                "createdAt": "2022-06-07T07:02:47.713123384Z",
                "updatedAt": "2022-06-07T07:02:47.713123546Z",
                "createdBy": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "updatedBy": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "versions": [],
                "operations": [],
                "owner": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "versionNumber": 1
            },
            "selfLink": "mavq:objects://tenants/admin/object_fields/abcprojects-emailfield"
        },
        "tenant": "admin",
        "uid": "abcprojects-emailfield"
    },
    "spec": {
        "objectConfigurationUri": "mavq:objects://tenants/admin/object_configurations/abcprojects",
        "display": {
            "description": "",
            "helpText": "",
            "label": "emailfieldupdated",
            "placeholder": ""
        },
        "definition": {
            "type": "EMAIL",
            "name": "emailfieldupdated",
            "mandatory": True,
            "indexing": False,
            "immutable": False,
            "unique": True,
            "allowedDomains": [
                "mavq.com"
            ]
        }
    }
}

FIELD_SEARCH_QUERY = {
    "config": {
        "type": "PAGE",
        "count": True
    },
    "matchers": {
        "equality": {
            "spec.objectConfigurationUri": "mavq:objects://tenants/admin/object_configurations/{objectId}",
            "metadata.system.controls.access.hidden": False
        },
        "columns": [],
        "from": []
    }
}

LAYOUT_CREATE = {
    "kind": "ObjectLayoutV2",
    "apiVersion": "objects.mavq.io/v1",
    "metadata": {
        "tenant": "admin"
    },
    "spec": {
        "name": "pythonlayout",
        "description": "",
        "primaryObject": "mavq:objects://tenants/admin/object_configurations/abcprojects",
        "layoutContainers": {
            "quickCreateLayout": {
                "apiLayout": {
                    "objectName": "abcprojects",
                    "relatedField": None,
                    "fields": [
                        "name",
                        "id"
                    ],
                    "relatedObjects": [
                        {
                            "objectName": "users",
                            "relatedField": "owner",
                            "fields": [
                                "name"
                            ],
                            "relatedObjects": None
                        }
                    ]
                },
                "displayConfig": {},
                "validations": [],
                "buttons": []
            },
            "detailLayout": {
                "apiLayout": {
                    "objectName": "abcprojects",
                    "relatedField": None,
                    "fields": [
                        "name",
                        "id"
                    ],
                    "relatedObjects": [
                        {
                            "objectName": "users",
                            "relatedField": "owner",
                            "fields": [
                                "name"
                            ],
                            "relatedObjects": None
                        }
                    ]
                },
                "displayConfig": {},
                "validations": [],
                "buttons": []
            }
        }
    }
}

LAYOUT_UPDATE = {
    "kind": "ObjectLayoutV2",
    "apiVersion": "objects.mavq.io/v1",
    "metadata": {
        "tenant": "admin"
    },
    "spec": {
        "name": "pythonlayoutUpdated",
        "description": "hello",
        "primaryObject": "mavq:objects://tenants/admin/object_configurations/abcprojects",
        "layoutContainers": {
            "quickCreateLayout": {
                "apiLayout": {
                    "objectName": "abcprojects",
                    "relatedField": None,
                    "fields": [
                        "name",
                        "id"
                    ],
                    "manyToManyFields": [],
                    "relatedObjects": [
                        {
                            "objectName": "users",
                            "relatedField": "owner",
                            "fields": [
                                "name"
                            ],
                            "manyToManyFields": [],
                            "relatedObjects": []
                        }
                    ]
                },
                "displayConfig": {},
                "validations": [],
                "buttons": []
            },
            "detailLayout": {
                "apiLayout": {
                    "objectName": "abcprojects",
                    "relatedField": None,
                    "fields": [
                        "name",
                        "id"
                    ],
                    "manyToManyFields": [],
                    "relatedObjects": [
                        {
                            "objectName": "users",
                            "relatedField": "owner",
                            "fields": [
                                "name"
                            ],
                            "manyToManyFields": [],
                            "relatedObjects": []
                        }
                    ]
                },
                "displayConfig": {},
                "validations": [],
                "buttons": []
            }
        }
    }
}

LAYOUT_SEARCH_QUERY = {}

RECORDTYPE_CREATE = {
    "kind": "ObjectRecordType",
    "apiVersion": "objects.mavq.io/v1",
    "metadata": {
        "tenant": "admin"
    },
    "spec": {
        "name": "pythonrectype",
        "description": "",
        "active": False,
        "layoutAssignments": [
            {
                "profileUri": "mavq:core://tenants/admin/profiles/administrator",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-newlayout12"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/demoprofile",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/dhanashri",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/dssdsdsds",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/gami",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-newlayout123"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/nag",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/profiledemo",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/ritu",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/sayanka",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/standard-user",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/vinodh",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/vishal",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            }
        ],
        "label": "pythonrectype",
        "objectConfigurationUri": "mavq:objects://tenants/admin/object_configurations/abcprojects"
    }
}

RECORDTYPE_UPDATE = {
    "kind": "ObjectRecordType",
    "apiVersion": "objects.mavq.io/v1",
    "metadata": {
        "system": {
            "controls": {
                "access": {
                    "readOnly": False,
                    "hidden": False,
                    "nonDeletable": False
                }
            },
            "hooks": [],
            "audit": {
                "createdAt": "2022-06-07T10:46:20.883Z",
                "updatedAt": "2022-06-07T10:46:20.883Z",
                "createdBy": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "updatedBy": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "versions": [],
                "operations": [],
                "owner": "mavq:core://tenants/admin/users/vishal-agarwal-back",
                "versionNumber": 1
            },
            "selfLink": "mavq:objects://tenants/admin/object_record_types/abcprojects-pythonrectype"
        },
        "tenant": "admin",
        "uid": "abcprojects-pythonrectype"
    },
    "spec": {
        "name": "pythonrecordtypeupdate",
        "description": "",
        "layoutAssignments": [
            {
                "profileUri": "mavq:core://tenants/admin/profiles/administrator",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-newlayout12"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/demoprofile",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/dhanashri",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/dssdsdsds",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/gami",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-newlayout123"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/nag",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/profiledemo",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/ritu",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/sayanka",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/standard-user",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/vinodh",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            },
            {
                "profileUri": "mavq:core://tenants/admin/profiles/vishal",
                "layoutUri": "mavq:objects://tenants/admin/object_layouts_v2/abcprojects-system"
            }
        ],
        "label": "pythonrecordtypeupdate",
        "objectConfigurationUri": "mavq:objects://tenants/admin/object_configurations/abcprojects"
    }
}

RECORDTYPE_SEARCH_QUERY = {
    "config": {
        "type": "PAGE",
        "count": True
    },
    "matchers": {
        "equality": {
            "spec.objectConfigurationUri": "mavq:objects://tenants/admin/object_configurations/abcprojects",
            "metadata.system.controls.access.hidden": False
        },
        "columns": [],
        "from": []
    }
}

RECORD_CREATE = {
    "complaints": {
        "objectName": "complaints",
        "fields": {
            "id": None,
            "name": "python",
            "createdAt": None,
            "updatedAt": None,
            "recordType": "system",
            "status": "active",
            "email": "vishal.agarwal@mavq.com"
        },
        "relatedObject": [],
        "manyManyItems": {},
        "mode": "CREATE"
    }
}

RECORD_UPDATE = {
    "complaints": {
        "objectName": "complaints",
        "fields": {
            "owner": None,
            "name": "python",
            "meta": None,
            "id": "{recordId}",
            "recordType": None,
            "updatedBy": None,
            "status": "active",
            "createdBy": None,
            "createdAt": None,
            "updatedAt": None,
            "email": "vishal.agarwal@mavq.com"
        },
        "relatedObject": [],
        "manyManyItems": {},
        "mode": "UPDATE"
    }
}

RECORD_SEARCH_QUERY = {
    "type": "OQL",
    "oql": {
        "config": {
            "type": "RAW_VIA_LAYOUT",
            "count": True,
            "pagination": {
                "limit": 10,
                "skip": 0
            }
        },
        "query": {
            "columns": [],
            "from": [],
            "where": None,
            "orderby": [
                {
                    "expr": {
                        "type": "column_ref",
                        "column": "updatedAt",
                        "table": "complaints",
                        "alias": "complaints"
                    },
                    "type": "DESC"
                }
            ]
        },
        "apiLayout": {
            "objectName": "complaints",
            "relatedField": None,
            "fields": [
                "name",
                "updatedAt"
            ],
            "manyToManyFields": [],
            "relatedObjects": [
                {
                    "objectName": "users",
                    "relatedField": "updatedBy",
                    "fields": [
                        "name"
                    ],
                    "manyToManyFields": [],
                    "relatedObjects": []
                },
                {
                    "objectName": "users",
                    "relatedField": "owner",
                    "fields": [
                        "name"
                    ],
                    "manyToManyFields": [],
                    "relatedObjects": []
                }
            ]
        }
    }
}