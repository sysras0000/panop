
var table_id = "campaign_table";

var selected_config;
var selected_data;

// make sure I have only one timer for polling
var polling_timer;

// number of times the database has been polled
var poll_count;

// number of times to poll the database then stop to build report
var poll_max;

// polling or error
var current_state;

function add_ids_to_table() {

    var row_count = 0;
    $('#' + table_id + ' thead tr').each(function () {
        var column_count = 0;
        $('th', this).each(function () {
            var temp_id = "th_" + row_count + "_" + column_count;
            $(this).attr("id", temp_id);
            column_count++;
        });
    });

    row_count = 1;

    $('#' + table_id + ' tbody tr').each(function () {
        var column_count = 0;
        $('td', this).each(function () {
            var temp_id = "td_" + row_count + "_" + column_count;
            $(this).attr("id", temp_id);
            column_count++;
        });
        row_count++;
    });

}

function hide_columns(add_timestamp_column) {

    if (add_timestamp_column) {
        columns_list_str = columns_list_str + "timestamp";
    }

    var incoming_list = columns_list_str.split("|");

    // create a list of all of the headers
    var all_header_names_list = [];

    $('#' + table_id + ' thead tr').each(function () {
        $('th', this).each(function () {
            all_header_names_list.push($(this).text());
        });
    });

    // read through the all_header_names_list
    // if the value is not in the incoming_list, add it to the hide_list
    var hide_list = [];

    for (var header_index = 0; header_index < all_header_names_list.length; header_index++) {

        var header_name = all_header_names_list[header_index].toLowerCase().trim();
        var found = false;

        for (var incoming_index = 0; incoming_index < incoming_list.length; incoming_index++) {
            var incoming_value = incoming_list[incoming_index].toLowerCase().trim();
            if (header_name === incoming_value) {
                found = true;
                break;
            }
        }

        if (!found) {
            hide_list.push(header_name);
        }
    }

    // displaying the data for the results means removing columns for several rows
    var number_of_rows = $("#" + table_id + " > tbody > tr").length;

    for (var hide_index = 0; hide_index < hide_list.length; hide_index++) {
        var hide_column_name = hide_list[hide_index];

        var temp_id = get_header_column_id_by_column_name(hide_column_name);
        if (temp_id < 0) {
            alert("Error in temp_id");
        }
        var temp_array = temp_id.split('_');
        var column_number = temp_array[2];

        $("#" + temp_id).hide();

        // hide the data columns
        for (var row_index = 0; row_index < number_of_rows; row_index++) {
            $("#" + "td_" + (row_index + 1) + "_" + column_number).hide();
        }
    }

}

// get the id of the header columns
function get_header_column_id_by_column_name(column_name) {

    var temp_id = -1;

    column_name = column_name.toLowerCase().trim();

    $('#' + table_id).find('th').each(function ($index) {
        var temp_name = $(this).text().toLowerCase().trim();
        if (temp_name === column_name) {
            temp_id = $(this).attr('id');
        }
    });
    return temp_id;
}

function process_state() {

    if (current_state === "poll_results" || current_state === "polling_error") {

        if (polling_timer === undefined) {

            selected_config = '{{ config_name | safe }}';
            selected_data = '{{ data_name | safe }}';

            var poll_seconds = '{{ poll_seconds | safe }}';

            if (poll_seconds === undefined) {
                poll_seconds = 60;
            }
            var poll_milliseconds = poll_seconds * 1000;

            polling_timer = setInterval(polling_database, poll_milliseconds);

            var poll_total_minutes = '{{ poll_total_minutes | safe }}';

            if (poll_total_minutes === undefined) {
                poll_total_minutes = 30;
            }
            poll_count = 1;
            poll_max = (poll_total_minutes * 60) / poll_seconds;

        } else {
            poll_count++;
        }

        $("#count_display").text("Poll Max: " + poll_max + " - Poll Count: " + poll_count);

    }

    if (current_state === "polling_error") {
        $("#error_div").show();
    } else {
        $("#error_div").hide();
    }

}

function populate_table(json_str) {

    $("#table_header").html("");
    $("#table_data").html("");

    var json_object = JSON.parse(json_str);

    // reset the header list since the table is empty
    if (current_state === "polling_error") {
        reset_column_list(json_object);
    }

    populate_table_header(json_object);
    populate_table_rows(json_object);

    add_ids_to_table();

    hide_columns(true);

}

function populate_table_rows(json_object) {

    var tbody_rows_list = json_object["tbody_rows"];

    var table_rows_list = [];

    for (var index = 0; index < tbody_rows_list.length; index++) {
        var temp_row = tbody_rows_list[index];
        table_rows_list.push(temp_row);
    }

    var table_rows = "";
    for (var row_index = 0; row_index < table_rows_list.length; row_index++) {

        var temp_row = table_rows_list[row_index];
        var temp_list = temp_row.split("|");

        var row_output = "<tr>";
        for (var column_index = 0; column_index < temp_list.length; column_index++) {
            var temp_value = temp_list[column_index];
            if (temp_value !== undefined && temp_value.length > 0) {
                row_output = row_output + "<td>" + temp_list[column_index] + "</td>";
            }
        }
        row_output = row_output + "</tr>";
        table_rows = table_rows + row_output;
    }

    $("#table_data").html("").append(table_rows);
}

function populate_table_header(json_object) {

    var thead_element = json_object["thead_row"];

    var table_rows_list = [];

    for (var index = 0; index < thead_element.length; index++) {
        var temp_row = thead_element[index];
        table_rows_list.push(temp_row);
    }

    var header_row = "";
    for (var row_index = 0; row_index < table_rows_list.length; row_index++) {

        var temp_row = table_rows_list[row_index];
        var temp_list = temp_row.split("|");

        var row_output = "";
        for (var column_index = 0; column_index < temp_list.length; column_index++) {
            row_output = row_output + "<th>" + temp_list[column_index] + "</th>";
        }

        header_row = "<tr>" + row_output + "</tr>";
    }

    $("#table_header").html("").append(header_row);

}

function reset_column_list(json_object) {

    var show_element = json_object["show_columns"];
    columns_list_str = show_element;
}

function display_object(temp_object, message) {

    var hyphens = '------------------------------------------';
    var output = hyphens + '\n';

    if (message !== undefined) {
        output = output + message + "\n" + hyphens + "\n";
    }

    for (var key in temp_object) {
        if (temp_object.hasOwnProperty(key)) {
            output += key + ':  ' + temp_object[key] + '\n';
        }
    }
    output += hyphens;

    alert(output);
}

