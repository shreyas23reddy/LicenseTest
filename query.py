import json

class queryPayload():

    def statsIFAgg(systemIP, interface, duration = "2", interval = 30):
        data = {"query":
{"condition": "AND",
    "rules": [
      {
        "value": [],
        "field": "entry_time",
        "type": "date",
        "operator": "last_n_hours"
      },
      {
        "value": [],
        "field": "vdevice_name",
        "type": "string",
        "operator": "in"
      },
      {
        "value": [],
        "field": "interface",
        "type": "string",
        "operator": "in"
      }
    ]
  },
  "sort": [
    {
      "field": "entry_time",
      "type": "date",
      "order": "asc"
    }
  ],
  "aggregation": {
    "field": [
      {
        "property": "interface",
        "sequence": 1
      }
    ],
    "histogram": {
      "property": "entry_time",
      "type": "minute",
      "interval": interval,
      "order": "asc"
    },
    "metrics": [
      {
        "property": "rx_kbps",
        "type": "avg"
      },
      {
        "property": "tx_kbps",
        "type": "avg"
      }
    ]
  }
}
        data["query"]["rules"][0]["value"].append(duration)
        data["query"]["rules"][1]["value"].append(systemIP)
        data["query"]["rules"][2]["value"].append(interface)
        data["aggregation"]["histogram"]["interval"] = interval
        return data
