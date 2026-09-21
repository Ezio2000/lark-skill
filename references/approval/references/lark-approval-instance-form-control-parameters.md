<a id="审批实例表单控件参数"></a>
# Approval Instance Form Control Parameters

> Note: This document aims to preserve the original structure and examples of the upstream parameter documentation as much as possible, to answer "what does control `value` look like".
> The currently recommended value conventions for `lark-cli` are governed by [`lark-approval-instance-value-sourcing.md`](./lark-approval-instance-value-sourcing.md); if the two documents differ on "where the value comes from", the latter takes precedence.

When calling the create approval instance API, you need to use form control parameters. This document helps you understand the parameter descriptions for each form control within an approval instance.

<a id="准备工作"></a>
## Preparation

The form control parameters of an approval instance are configured based on the approval definition form. For example, if the approval definition's form design includes **Single-line text** and **Date interval** controls, then the approval instance's form control parameters need to assign values for the **Single-line text** and **Date interval** controls. Therefore, before operating on the control parameters of an approval instance form, you should first confirm the form control structure through the approval definition details.

<a id="审批实例-api-不支持的控件"></a>
## Controls Not Supported by the Approval Instance API

The create approval instance API does not fully support all approval form controls. The unsupported controls are shown in the table below. If you must use a control that the API does not support, you cannot complete the submission through the current API alone.

**Control/Control Group** | **Type**                    |
| ---------- | --------------------------- |
| Description         | text                        |
| Reference to Base     | mutableGroup                |
| Receiving Account       | account                     |
| Serial Number        | serialNumber                |
| Business Trip Control Group      | tripGroup                   |
| Onboarding Control Group      | apaascorehrOnboardingGroup  |
| Regularization Control Group      | apaascorehrRegularateGroup  |
| Attendance Makeup Control Group      | remedyGroupV2               |
| Job Adjustment Control Group      | apaascorehrJobAdjustGroup   |
| Offboarding Control Group      | apaascorehrOffboardingGroup

<a id="通用参数"></a>
## Common Parameters

The parameters common to all form controls of an approval instance are shown in the table below.

Parameter | Type | Required | Description
---|---|---|---
id | string | Yes | The control's ID, which must match the control ID in the approval definition.
type | string | Yes | Control type. For the values of each control type, see the **Parameters for Different Controls** section below.
value | Varies by control type | Yes | The control's value. The value data type also varies by control; for example, the value of a single-line text control is a string, and the value of a contact is an array. For details, see the **Parameters for Different Controls** section below.

<a id="不同控件的参数"></a>
## Parameters for Different Controls

This section provides the type parameter values, JSON examples, and non-common parameter descriptions for different controls.

<a id="单行文本"></a>
### Single-line Text

The control type is input. JSON data example:

```json
{
    "id": "widget1",
    "type": "input",
    "value": "data" // string type
}
```

<a id="多行文本"></a>
### Multi-line Text

The control type is textarea. JSON data example:

```json
{
    "id": "widget1",
    "type": "textarea",
    "value": "data" // string type
}
```

<a id="日期"></a>
### Date

The control type is date. JSON data example:

```json
{
    "id": "widget1",
    "type": "date",
    "value": "2019-10-01T08:12:01+08:00" // string type that must conform to the RFC3339 format
}
```

<a id="日期区间"></a>
### Date Interval

The control type is dateInterval. JSON data example:

```json
{
    "id": "widget1",
    "type": "dateInterval",
    "value": {
         "start":"2019-10-01T08:12:01+08:00",
         "end":"2019-10-02T08:12:01+08:00",
         "interval": 1.0
     }
}
```

The value parameter is of object type. Parameter descriptions:

Parameter | Type | Required | Description
---|---|---|---
start | string | Yes | Start time, which must conform to the RFC3339 format.
end | string | Yes | End time, which must conform to the RFC3339 format.
interval | float | Yes | Duration (days).

<a id="单选"></a>
### Single Select

The control type is radio/radioV2. JSON data example:

```json
{                                     
    "id": "widget1",
    "type": "radioV2",
    "value": "k2b8mkx0-h71x5gl1234-1" // string type
}
```

Here, value represents the option value, and the value range needs to reference the value parameter of the **Single Select** control's option in the corresponding approval definition. You can obtain the value of the single select control's option through the `form` parameter returned by the approval definition details. If the control is associated with an external option, then value needs to be passed the `options.id` of the external option.

<a id="多选"></a>
### Multi-select

The control type is checkbox/checkboxV2. JSON data example:

```json
{
    "id":"widget1",
    "type":"checkboxV2",
    "value": ["k2b8mkx0-h71x5gl4321-1"] // array of string type
}
```
Here, value represents the option value, and the value range needs to reference the value parameter of the **Multi-select** control's option in the corresponding approval definition. You can obtain the value of the multi-select control's option through the `form` parameter returned by the approval definition details. If the control is associated with an external option, then value needs to be passed the `options.id` of the external option.

<a id="数字"></a>
### Number

The control type is number. JSON data example:

```json
{
    "id": "widget1",
    "type": "number",
    "value": 1234.5678 // float type
}
```

<a id="金额"></a>
### Amount

The control type is amount. JSON data example:

```json
{
    "id": "widget1",
    "type": "amount",
    "value": 1234.5678, // float type
    "currency":"USD"
}
```

Here, currency represents the currency type, and the value range needs to reference the value parameter of the **Amount** control in the corresponding approval definition. You can obtain the currency types that can be set for the amount control through the `form` parameter returned by the approval definition details.

<a id="计算公式"></a>
### Formula

The control type is formula. JSON data example:

```json
{
    "id": "widget1",
    "type": "formula",
    "value": 1234.5678 // This value is calculated by the formula configured in the approval definition. If it does not match, an error will be returned.
}
```

<a id="联系人"></a>
### Contact

The control type is contact. JSON data example:

```json
{
    "id":"widget1",
    "type":"contact",
    "value": ["f8ca557e"], // array of string type
    "open_ids": ["ou_12345"] // array of string type
}
```
Here, value contains the user's `user_id`; open_ids contains the user's `open_id`.

<a id="关联审批"></a>
### Linked Approval

The control type is connect. JSON data example:

```json
{
    "id":"widget1",
    "type":"connect",
    "value": ["19EAC829-F1CB-527F-BE2A-1330422E60C0"] // array of string type
}
```
Here, value contains the Code of the linked approval instance. You can obtain the instance details by the instance Code through the approval instance details capability.

<a id="文档控件"></a>
### Document Control

The control type is document. JSON data example:

```json
{
    "id": "widget1",
    "type": "document",
    "value": {
           "token":"TLLKdcpDro9ijQxA33ycNMabcef",
           "type":"docx",
    }
}
```

The value parameter is of object type. Parameter descriptions:

Parameter | Type | Required | Description
---|---|---|---
token | string | Yes | The document's document_id.
type | string | Yes | Document type. Supports `docx`.

<a id="附件"></a>
### Attachment

The control type is attachmentV2. JSON data example:

```json
{
    "id":"widget1",
    "type":"attachmentV2",
    "value": ["D93653C3-2609-4EE0-8041-61DC1D84F0B5"] // array of string type
}
```
Here, value contains the file code returned after uploading the file.

<a id="图片"></a>
### Image

The control type is image/imageV2. JSON data example:

```json
{
    "id":"widget1",
    "type":"image",
    "value": ["D93653C3-2609-4EE0-8041-61DC1D84F0B5"] // array of string type
}
```

Here, value contains the file code returned after uploading the file.

<a id="明细表格"></a>
### Detail/Table

The control type is fieldList. JSON format example:

```json
{
    "id": "widget1",
    "type": "fieldList",
    "value": [
         [   
            {
                "id": "widget1",
                "type": "checkbox",
                "value": ["jxpsebqp-0"]
            }
         ]
     ]
}
```

Here, value is a two-dimensional array. Set the control JSON values in order according to the controls contained in the **Detail/Table** control within the approval definition.

<a id="部门"></a>
### Department

The control type is department. JSON data example:

```json
{
    "id":"widget1",
    "type":"department",
    "value":[ 
        {
            "open_id": "od-xxx"
        }
    ]
}
```

Here, value is an array of objects. Set the department's open_department_id through open_id.

<a id="电话"></a>
### Phone

The control type is telephone. JSON data example:

```json
{
    "id":"widget1",
    "type":"telephone",
    "value": {
        "countryCode":"+86",
        "nationalNumber":"13122222222"
    }
}
```

The value parameter is of object type. Parameter descriptions:

Parameter | Type | Required | Description
---|---|---|---
countryCode | string | Yes | Area code.
nationalNumber | string | Yes | Phone number.

<a id="地址"></a>
### Address
The control type is address. JSON data example:

```json
{
	"id": "widget1",
	"type": "address",
	"value": [{
		"id": "290557",
		"detailAddress": "详细的地址"
	}]
}
```

The value parameter is of []object type. Parameter descriptions are as follows:

Parameter | Type | Required | Description
---|---|---|---
value | []object | Yes | In non-business-trip control group scenarios, the address control only supports a single address; when multiple are passed, only the first is taken by default
└ id | string | Yes | Region ID, which can be obtained through the approval's geographic library API
└ detailAddress | string | No | Detailed address. If filling in a detailed address is not enabled in the form configuration, this parameter will be ignored and will not take effect even if passed

<a id="换班控件组"></a>
### Shift Swap Control Group

The control type is shiftGroup. JSON data example:

```json
{
    "id": "widget1",
    "type": "shiftGroup",
    "value": {
         "shiftTime": "2019-10-01T08:12:01+08:00",
         "returnTime": "2019-10-02T08:12:01+08:00",
         "reason": "ask for leave"
     }
}
```

The value parameter is of object type. Parameter descriptions:

Parameter | Type | Required | Description
---|---|---|---
shiftTime | string | Yes | Shift swap time, which must conform to the RFC3339 format.
returnTime | string | Yes | Swap date, which must conform to the RFC3339 format.
reason | string | Yes | Reason for shift swap.

<a id="请假控件组"></a>
### Leave Control Group

**Leave control group request example**
```json
{
    "id": "widgetLeaveGroupV2",
    "type": "leaveGroupV2",
    "value": [
      {
        "id": "widgetLeaveGroupType",
        "type": "radioV2",
        "value": "7488925543484620819"
      },
      {
        "id": "widgetLeaveGroupStartTime",
        "type": "date",
        "value": "2025-08-25T11:30:00+08:00"
      },
      {
        "id": "widgetLeaveGroupEndTime",
        "type": "date",
        "value": "2025-08-26T11:35:00+08:00"
      },
      {
        "id": "widgetLeaveGroupReason",
        "type": "textarea",
        "value": "123123"
      },
      {
        "id": "widgetLeaveCertification",
        "type": "image",
        "value": [
          "B69F8E26-0EAA-4A92-9B80-DA613CD36136"
        ]
      },
      {
        "id":"widgetLeaveCertification",
        "type":"image",
        "value": ["D93653C3-2609-4EE0-8041-61DC1D84F0B5"]
      },
      {                                     
        "id": "widgetLeaveGroupFeedingArrivingLate",
        "type": "radioV2",
        "value": "30"
      },
      {                                     
        "id": "widgetLeaveGroupFeedingOffLeaveEarly",
        "type": "radioV2",
        "value": "30"
      }        
    ]
}
```

**Leave control group parameter descriptions:**

id | Type | JSON Example | Description
---|---|---|---
id | string | Yes | Control group ID, fixed as widgetLeaveGroupV2
type | string | Yes | Control group type, fixed as leaveGroupV2
value | object[] | Yes | The value of the control group, which is a list of multiple sub-control values

Description of the sub-control values contained in value:

id | Type | JSON Example | Description
---|---|---|---
widgetLeaveGroupType | radioV2 | ```<br>{<br>"id": "widgetLeaveGroupType",<br>"type": "radioV2",<br>"value": "7488925543484620819"<br>}<br>``` | Leave type. For the specific format, refer to the single select control. The options are obtained through the attendance API. This control must be included when submitting
widgetLeaveGroupStartTime | date | ```<br>{<br>"id": "widgetLeaveGroupStartTime",<br>"type": "date",<br>"value": "2019-10-01T08:12:01+08:00", // string type that must conform to the RFC3339 format<br>}    <br>``` | Leave start time. For the specific format, refer to the date control. It will be automatically rounded according to the leave type. For half-day leave, if it is earlier than 12 o'clock, it is considered morning; for hourly leave, it is rounded forward to the nearest half hour. This control must be included when submitting
widgetLeaveGroupEndTime | date | ```<br>{<br>"id": "widgetLeaveGroupEndTime",<br>"type": "date",<br>"value": "2019-10-01T08:12:01+08:00", // string type that must conform to the RFC3339 format<br>}<br>``` | Leave end time. For the specific format, refer to the date control. It will be automatically rounded according to the leave type. For half-day leave, if it is earlier than 12 o'clock, it is considered morning; for hourly leave, it is rounded backward to the nearest half hour
widgetLeaveGroupReason | textarea | ```<br>{<br>"id": "widgetLeaveGroupReason",<br>"type": "textarea",<br>"value": "123123"<br>}<br>``` | Leave reason. For the specific format, refer to the multi-line text control. It is not required for breastfeeding leave; in other cases, it is determined by whether the control is visible and required in the control group configuration
widgetLeaveCertification | image | ```<br>{<br>"id":"widgetLeaveCertification",<br>"type":"image",<br>"value": ["D93653C3-2609-4EE0-8041-61DC1D84F0B5"]<br>}<br>``` | Leave certificate. For the specific format, refer to the image control. If the configuration of the selected leave type requires supplementary proof, this value must be passed; otherwise an error will be reported
widgetLeaveGroupFeedingArrivingLate | radioV2 | ```<br>{                                     <br>"id": "widgetLeaveGroupFeedingArrivingLate",<br>"type": "radioV2",<br>"value": "30"<br>}<br>``` | Number of minutes late for work. For the specific format, refer to the single select control. Only required for breastfeeding leave. The value range is 0-120 minutes, with a granularity of 15 minutes. The options are obtained from the option of this control in the approval definition
widgetLeaveGroupFeedingOffLeaveEarly | radioV2 | ```<br>{                                     <br>"id": "widgetLeaveGroupFeedingOffLeaveEarly",<br>"type": "radioV2",<br>"value": "30"<br>}   <br>``` | Number of minutes leaving work early. For the specific format, refer to the single select control. Only required for breastfeeding leave. The value range is 0-120 minutes, with a granularity of 15 minutes. The options are the strings corresponding to the minutes

**Special parameter validation error messages**
message                                            | Description                           |
| -------------------------------------------------- | ---------------------------- |
| leave type id parse error                          | Leave type is not int64                  |
| group value is invalid                             | The current control group value is invalid. Please check whether it is empty or whether the type is an array |
| start time format is not RFC3339                   | The start time date format is not *RFC3339 format*         |
| end time format is not RFC3339                     | The end time date format is not *RFC3339 format*         |
| start time is after end time                       | Start time is later than end time                   |
| user not in gray                                   | The applying user is not in the attendance gray release                  |
| leave type not found                               | Leave type does not exist                      |
| reason is required                                 | Leave reason is not filled in                      |
| leave quote should be bigger than 0                | Leave duration must be greater than 0                    |
| leave is conflict                                  | There is already a leave record within the selected time. Please choose another time          |
| balance is not enough                              | Insufficient leave balance under the current leave type                |
| certification is required                          | Leave certificate needs to be uploaded                     |
| arriving late is required                          | Breastfeeding leave requires filling in the late arrival duration                |
| arriving late value is not in the optional items   | The late arrival time is not within the selectable range                  |
| leaving early is required                          | Breastfeeding leave requires filling in the early departure duration                |
| leaving early value is not in the optional items   | The early departure time is not within the selectable range                |
| feeding rest daily is 0                            | The daily rest duration for breastfeeding leave is 0. Please reselect            |
| the operation is prohibited by the workforce rules | The current account has been closed on the attendance side and cannot be submitted

<a id="加班控件组"></a>
### Overtime Control Group

**Overtime control group request example**
```json
{
  "id": "widgetWorkGroup",
  "type": "workGroup",
  "value":[
    {
      "id":"widgetWorkGroupOvertimeWorkers",
      "type":"contact",
      "value": ["f8ca557e"],
      "open_ids": ["ou_12345"]
    },
    {
      "id": "widgetWorkGroupType",
      "type": "radioV2",
      "value": "7259635026038505475"
    },
    {
      "id":"widgetWorkGroupTimeRangeFieldList",
      "type":"fieldList",
      "value":[
        [
          {
            "id":"widgetWorkGroupStartTime",
            "type":"date",
            "value":"2019-10-01T08:12:01+08:00"
          },
          {
            "id":"widgetWorkGroupEndTime",
            "type":"date",
            "value":"2019-10-01T08:12:01+08:00"
          }
        ]
      ]
    },
    {
      "id": "widgetWorkGroupReason",
      "type": "textarea",
      "value": "111"
    }
  ]
}

```

**Overtime control group parameter descriptions:**

Parameter | Type | Required | Description
---|---|---|---
id | string | Yes | Control group ID, fixed as widgetWorkGroup
type | string | Yes | Control group type, fixed as workGroup
value | object[] | Yes | The value of the control group, which is a list of multiple sub-control values

Description of the sub-control values contained in value:

id | Type | JSON Example | Description
---|---|---|---
widgetWorkGroupOvertimeWorkers | contact | ```<br>{<br>"id":"widgetWorkGroupOvertimeWorkers",<br>"type":"contact",<br>"value": ["f8ca557e"], <br>"open_ids": ["ou_12345"]<br>}<br>``` | Overtime worker list. For the specific format, refer to the contact control. If "Allow submitting on behalf of multiple people" is configured in the definition, this field is required. If the submitter is submitting for themselves, the submitter's ID must be filled in
widgetWorkGroupType | radioV2 | ```<br>{<br>"id": "widgetWorkGroupType",<br>"type": "radioV2",<br>"value": "7259635026038505475" // corresponding type option ID<br>}<br>``` | Overtime type. For the specific format, refer to the single select control. If "Associate overtime rules" is disabled in the definition, this field needs to be filled in
widgetWorkGroupTimeRangeFieldList | fieldList | ```<br>{<br>"id":"widgetWorkGroupTimeRangeFieldList",<br>"type":"fieldList",<br>"value":[<br>[<br>{<br>"id":"widgetWorkGroupStartTime",<br>"type":"date",<br>"value":"2019-10-01T08:12:01+08:00"<br>},<br>{<br>"id":"widgetWorkGroupEndTime",<br>"type":"date",<br>"value":"2019-10-01T08:12:01+08:00"<br>}<br>]<br>]<br>}<br>``` | Overtime time period. For the specific format, refer to the detail control. If "Allow submitting multiple overtime time periods" is enabled in the definition, multiple can be passed, up to 30; otherwise only the first will be taken. A single overtime duration cannot exceed two days
widgetWorkGroupReason | textarea | ```<br>{<br>"id": "widgetWorkGroupReason",<br>"type": "textarea",<br>"value": "111"<br>}<br>``` | Overtime reason. If "Overtime reason" is configured as required in the definition, this field must be filled in

**Special parameter validation error messages**
message                                                                            | Description                           |
| ---------------------------------------------------------------------------------- | ---------------------------- |
| the time range list has more than 30 items                                         | The number of overtime time periods exceeds 30                   |
| group value is invalid                                                             | The current control group value is invalid. Please check whether it is empty or whether the type is an array |
| overtime type is required                                                          | When overtime rules are not associated, overtime type is required              |
| work time range is required                                                        | At least one overtime time period is required                   |
| start time is after end time                                                       | Start time is later than end time                   |
| start time or end time of range is required                                        | The start time and end time of the overtime time period are required            |
| overtime duration is over 2 days                                                   | A single overtime duration cannot exceed two days                 |
| overtime date time zone not support                                                | The date time zone information of the overtime time period cannot be recognized              |
| {date} can not apply overtime                                                      | Overtime cannot be applied for the selected time                   |
| {date} already apply overtime                                                      | There is already an overtime record for the selected time                  |
| {date} no need approval                                                            | Overtime on the selected date does not require application                   |
| apply reason is required                                                           | The definition sets the overtime reason as required and it cannot be empty           |
| {users} user follow different overtime rules, cannot be submitted in the same form | The selected overtime workers are not in the same attendance group and cannot submit overtime at the same time      |
| invalid overtime work application                                                  | There is no valid overtime application. Please reselect the overtime date          |
| the overtime duration cannot be 0                                                  | Overtime duration cannot be 0                     |
| the number of apply workers cannot exceed 50                                       | The number of overtime workers in a single application cannot exceed 50              |
| apply worker is required                                                           | There must be an overtime worker. When configured to allow submitting on behalf of multiple people, the overtime worker must be specified     |
| resigned worker can not apply                                                      | Resigned personnel cannot apply for overtime                   |
| overtime duration is over limit                                                    | Overtime duration exceeds the limit

<a id="外出控件组"></a>
### Outing Control Group

**Outing control group request body example**
```json
{
    "id": "widgetOutGroup",
    "type": "outGroup",
    "value":[
        {
            "id": "widgetOutGroupType",
            "type": "radioV2",
            "value":  "me15yqrf-gmjgbml2vhp-0"      
        },
        {
            "id": "widgetOutGroupStartTime",
            "type": "date",
            "value":"2019-10-01T08:12:01+08:00"
        },
        {
            "id": "widgetOutGroupEndTime",
            "type": "date",
            "value":"2019-10-01T08:12:01+08:00"
        },
        {
            "id": "widgetOutGroupReason",
            "type": "textarea",
            "value":"123213"
        },
        {
            "id":"widgetOutGroupImage",
            "type":"image",
            "value": ["D93653C3-2609-4EE0-8041-61DC1D84F0B5"]
        }                    
    ]   
}

```

**Outing widget parameter description**

Parameter | Type | Required | Description
---|---|---|---
id | string | Yes | Widget group ID, fixed as widgetOutGroup
type | string | Yes | Widget group Type, fixed as outGroup
value | object[] | Yes | The value of the widget group, which is a list of values of multiple child widgets

Description of the child widget values contained in value:

id | Type | JSON example | Description
---|---|---|---
widgetOutGroupType | radioV2 | ```<br>{<br>"id": "widgetOutGroupType",<br>"type": "radioV2",<br>"value":  "me15yqrf-gmjgbml2vhp-0"      <br>}<br>``` | Outing type. For the specific format, refer to the radio widget. If "Outing type" is configured, this field is required. The outing duration unit will use the unit associated with the selected outing type. If "Outing type" is not configured, this field does not need to be filled in, and the unit configured for "Outing duration" will be used when calculating the outing duration
widgetOutGroupStartTime | date | ```<br>{<br>"id": "widgetOutGroupStartTime",<br>"type": "date",<br>"value":"2019-10-01T08:12:01+08:00"<br>}<br>``` | Outing start time. For the specific format, refer to the date widget. If the outing duration unit is half-day leave, then a time earlier than 12:00 is considered morning, otherwise it is considered afternoon; if the unit is hours, it will be rounded down to the nearest half hour
widgetOutGroupEndTime | date | ```<br>{<br>"id": "widgetOutGroupEndTime",<br>"type": "date",<br>"value":"2019-10-01T08:12:01+08:00"<br>}<br>``` | Outing end time. For the specific format, refer to the date widget. If the outing duration unit is half-day leave, then a time earlier than 12:00 is considered morning, otherwise it is considered afternoon; if the unit is hours, it will be rounded up to the nearest half hour
widgetOutGroupReason | textarea | ```<br>{<br>"id": "widgetOutGroupReason",<br>"type": "textarea",<br>"value":"123213"<br>}<br>``` | Outing reason. For the specific format, refer to the multiline text widget. If "Outing reason" is required in the definition, this widget must be filled in; if the definition is configured as not required, this widget does not need to be filled in
widgetOutGroupImage | image | ```<br>{<br>"id":"widgetOutGroupImage",<br>"type":"image",<br>"value": ["D93653C3-2609-4EE0-8041-61DC1D84F0B5"]<br>}   <br>``` | Outing proof. For the specific format, refer to the image widget. If "Outing photo" is required in the definition, this widget must be filled in; if the definition is configured as not required, this widget does not need to be filled in

**Special parameter validation error messages**

message                                               | Description                           |
| ----------------------------------------------------- | ---------------------------- |
| group value is invalid                                | The current widget group value is invalid. Please check whether it is empty or whether the validation type is an array |
| start time format is not RFC3339                      | The start time date format is not *RFC3339 format*         |
| end time format is not RFC3339                        | The end time date format is not *RFC3339 format*         |
| start time and end time must be in the same time zone | The start time and end time must be in the same time zone             |
| out type is required                                  | If "Outing type" is set in the definition, the outing type is required       |
| out start time is required                            | Outing start time is required                     |
| out end time is required                              | Outing end time is required                     |
| out duration must be greater than 0                   | The outing interval cannot be 0. Please check the start and end times and select again        |
| out reason is empty                                   | If "Outing reason" is checked in the definition and set as required, this field is required   |
| photo is required                                     | If "Outing photo" is checked in the definition and set as required, this field is required   |
| out time is conflict                                  | The outing time conflicts. Please confirm whether an outing has already been requested for this period
