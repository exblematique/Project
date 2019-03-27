# REST endpoints

All requests should append a prefix of `/api`. Meaning `/tablesections` would instead be `/api/tablesections`.

## Get all table sections

```
url:	/tablesections/
method:	GET
```

Example response:

```json
{
	"table_sections": [
		{
			"id": 1,
			"pos": [
				3, 5
			],
			"type": 1
		},
		{
			"id": 2,
			"pos": [
				5, 3
			],
			"type": 2
		}
	]
}
```
## Get information of a given table id
```
url:    /tablesections/:id/
Method: GET
```

Example response:

```json
{
  "id": 5,
  "pos": [
	9,
	8
  ],
  "type": 1,
  "voltage": 0
}
```
 

## Get all modules of a given table section

```
url:	/tablesections/:id/modules/
method: GET
```

Example response:

```json
{
	"modules": [
		{
			"id": 2090677472,
			"locationId": 0
		},
		{
			"id": 1945556720,
			"locationId": 1
		}
	]
}
```

## Get all modules

```
url:	/modules/
method:	GET
```

Example response:

```json
{
	"modules": [
		{
			"id": 3920381746
		},
		{
			"id": 2310312452
		}
	]
}
```

## Get info of a given module

```
url:	/modules/:id/
method:	GET
```

Example response:

```json
{
	"id": 3920381746,
	"name": "Nuclear Power Plant 2",
	"power": -500,
	"voltage": "High"
}
```

## Get configurations of a given module

```
url:	/modules/:id/configs/
method:	GET
```

Example response:

```json
{
	"configurations": [
		{
			"id": 9,
			"max": 1200,
			"min": 0,
			"name": "Generator",
			"role": "production",
			"value": 500
		}
	]
}
```

## Get given configuration of a given module

```
url:	/modules/:id/configs/:config_id/
method:	GET
```

Example response:

```json
{
	"id": 9,
	"max": 1200,
	"min": 0,
	"name": "Generator",
	"role": "production",
	"value": 500
}
```

## Set property of given configuration on a given module

```
url:	/modules/:id/configs/:config_id/
method:	PUT
```

Example request content:

```json
{
	"name": "Old Generator"
}
```

Example response:

```json
{
	"id": 9,
	"max": 1200,
	"min": 0,
	"name": "Old Generator",
	"role": "production",
	"value": 500
}
```

## Set a flow colour

The color is equivalent to certain voltages and loads.
```
| ID | Description    |
| -- | -------------- |
| 0  | low voltage    |
| 1  | medium voltage |
| 2  | high voltage   |
| 3  | normal load    | 
| 4  | high load      |
| 5  | stressed load  |
```

```
url:	/flowcolor/:id/
method:	PUT
```

Example request content:

```json
{
	"value": "ff0000"
}
```

## Get all currently used colors

The color is equivalent to certain voltages and loads.
```
| ID | Description    |
| -- | -------------- |
| 0  | low voltage    |
| 1  | medium voltage |
| 2  | high voltage   |
| 3  | normal load    |
| 4  | high load      |
| 5  | stressed load  |
```

```
url:	/flowcolor/
method:	GET
```

Example response:

```json
{
    "colors": [
        {
            "color": "19ccff",
            "id": 0
        },
        {
            "color": "994cff",
            "id": 1
        },
        {
            "color": "3319ff",
            "id": 2
        },
        {
            "color": "00ff00",
            "id": 3
        },
        {
            "color": "ffff00",
            "id": 4
        },
        {
            "color": "ff0000",
            "id": 5
        }
    ]
}
```

## Get powerboundaries for voltages and flows

```
url:	/powerboundaries/
method:	GET
```

Example response:

```json
{
	"boundaries": {
		"0": {
			"high": 0.75,
			"critical": 300
		},
		"1": {
			"high": 0.75,
			"critical": 500
		},
		"2": {
			"high": 0.75,
			"critical": 1300
		}
	}
}
```

* 0/1/2: voltages. 0 means low, 1 means medium, 2 means high
* High: modifier for high load
* Critical: absolute value for critical load

## Set one of the boundaries for load

```
url:	/powerboundaries/
method:	PUT
```

Example request content:

```json
{
	"voltage": 0,
	"load": 2,
	"value": 500
}
```

## Get the grid

```
url:	/grid/
method:	GET
```

Example response:

```json
{
	"flow_segments": [
		{
			"start_pos": [
			    9,
			    10
			],
			"end_pos": [
			    10,
			    10
			],
			"direction": 0,
			"enabled": true,
			"table_section": 6
		}
	],
	"modules": [
	    {
            "pos": [
                12,
                11
            ],
            "remainingPower": 0,
            "table_section": 6
        }
	]
}
```

Where `direction` is either 0 (forwards) or 1 (backwards).

## Get the grid data of a specific table id
```
url:    /grid/:table_id/
Method: GET
```

Example response:

```json
{
	"flow_segments": [
        {
          "direction": null,
          "enabled": true,
          "end_pos": [
            10,
            10
          ],
          "load": 0,
          "start_pos": [
            9,
            10
          ],
          "table_section": 5
        },
        {
          "direction": 1,
          "enabled": true,
          "end_pos": [
            10,
            9
          ],
          "load": 0,
          "start_pos": [
            10,
            10
          ],
          "table_section": 5
        }
    ]
}
``` 

## Get neighboring table
```
url:    /api/neighbours/:id/
method: GET
```

Example response

```json
{
    "bottom": null,
    "left": null,
    "right": 5,
    "top": 2
}
```

## Flowsegment

```
url:	/flowsegment/:table_id/:segment_id/
method:	PUT
```

Where id comes from `/grid/` in the "flow_segments" array (based on order of the result).

Exampe request content:

```json
{
	"enabled": "true"
}
```

## Reboot all table sections

```
url:	/reboot/
method:	PUT
```
