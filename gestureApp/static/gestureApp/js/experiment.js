const possible_states = {
    StartingExperiment: 'startingExperiment',
    WaitingStart: 'waitingStart',
    StartBlock: 'startBlock',
    DoingTrial: 'doingTrial',
    EndBlock: 'endBlock',
    StartRest: 'startRest',
    DoingRest: 'doingRest',
    EndExperiment: 'endExperiment',
    WaitSendData: 'waitSendData'
}

var current_state = possible_states.StartingExperiment;
// One array for each block
var experiment_trials = new Array()
var block_trials = new Array();
var trial_aux = {
    input_seq: "",
    initial_timestamp: 0.0,
    seq_timestamps: new Array(),
    time_limit: 0
}
var trial = Object.assign({}, trial_aux)
var timer = null
var experiment = JSON.parse(document.getElementById('experiment').textContent);
var blocks = JSON.parse(document.getElementById('blocks').textContent);
var sequences = JSON.parse(document.getElementById('sequences').textContent);
var resting_time = JSON.parse(document.getElementById('rest-time').textContent);
var timer_rest = null

// Current block
var current_block = 0

function runTrials()
{
    var n = blocks[current_block]['num_trials']
    trialStarts(n);
}

function trialStarts(n)
{
    // console.log("Starting trial")
    // Change html
    $("#trial-num").html(blocks[current_block]['num_trials'] - n + 1);
    $("#trials-left").html(n-1);

    // Restart the trial object
    trial = Object.assign({}, trial_aux);
    trial.seq_timestamps = new Array();

    // For the timer
    var starting_date = new Date().getTime();

    // Add the initial timestamp
    trial.initial_timestamp = starting_date;
    trial.time_limit = blocks[current_block].time_per_trial
    $("#time-left").html(trial.time_limit); 
    // console.log(trial.time_limit)
    
    // Trial ends after X milliseconds
    setTimeout(()=> trialEnds(n), trial.time_limit * 1000);
    $(document).keydown(keydownEvent)

    // Show timer
    timer = setInterval(() => {
        var now = new Date().getTime();
        var distance = (starting_date + trial.time_limit * 1000 - now) / 1000
        $("#time-left").html(Math.round(distance)); 
    }, 1000);
}

function keydownEvent(e)
{
    trial.input_seq += e.key;
    var timestamp = new Date().getTime();
    trial.seq_timestamps.push(timestamp)
}

function trialEnds(n)
{
    // Stop listening to keydown events
    $(document).off("keydown")

    // Reset timer
    $("#time-left").html(trial.time_limit); 
    clearInterval(timer)
    timer = null

    block_trials.push(Object.assign({}, trial))
    // console.log(JSON.stringify(trials))
    if (n - 1 > 0)
        trialStarts(n - 1);
    else
    {
        current_state = possible_states.StartRest;
    }
}

function sendData() {
    console.log("Sending data!");
    console.log(JSON.stringify(experiment_trials))
    $.ajax({
        type: "POST",
        url: '/ajax/create_trials',
        data: {
          'experiment_trials': JSON.stringify(experiment_trials),
          'experiment': experiment,
          'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
        },
        dataType: 'json',
        success: function (data) {
            console.log(data)
            // Clear old trials, to avoid sending them more than one time.
            experiment_trials = new Array();
        },
        error: function (xhr, status, error) {
            console.log("Error!!");
            console.log(xhr);
            console.log(status);
            console.log(error);
        }
      });

    
}

$(document).ready(function () 
{
    // When the webpage loads, we'll start a timer, and show in screen something like: 'Starting in 3,2,1...'
    $("#start-btn").click(()=>setInterval(doExperiment, 100))
})

function showStartMessage() {
    var seconds_left = 3
    var subs = function (next) {
        $("#start-message-number").text(seconds_left.toString());
        seconds_left--;
        next();
    }
    $("#div-content")
    .append("<p id='start-message'>Starting experiment in ... <b id='start-message-number'></b></p>")
    .queue(subs)
    .delay(1000)
    .queue(subs)
    .delay(1000)
    .queue(subs)
    .delay(1000)
    .queue((next) => {$("#start-message").remove(); next()})
    .queue(() => current_state = possible_states.StartBlock);

}

function doRest(){
    $("#time-left-rest").html(resting_time); 
    // For the timer
    var starting_date = new Date().getTime();

    // Show html
    $("#rest-info").show();

    // Rest ends after X milliseconds
    setTimeout(()=> {
        current_state = possible_states.EndBlock;
        $("#rest-info").hide();
    }, resting_time * 1000);

    // Show timer
    timer_rest = setInterval(() => {
        var now = new Date().getTime();
        var distance = (starting_date + resting_time * 1000 - now) / 1000
        $("#time-left-rest").html(Math.round(distance)); 
    }, 1000);
}


function doExperiment(next)
{
  switch (current_state) {
    case possible_states.StartingExperiment:
        $("#start-btn").hide();
        setTimeout(() => showStartMessage(), 1);
        current_state = possible_states.WaitingStart;
        break;
    case possible_states.StartBlock:
        //   Define and show the html content accordingly
        $("#experiment-info").show();
        $("#block-num").html(current_block + 1);
        $("#sequence").html(sequences[current_block]);
        // fill the trial object accordingly
        current_state = possible_states.DoingTrial;
        runTrials();
        //   console.log('Holaaa');
        // Start the trials
        break;
    case possible_states.EndBlock:
        //   Give rest, and then increase block index until no blocks are left.
        console.log('Block ended');
        clearInterval(timer_rest)
        timer_rest = null
        console.log(block_trials);
        // Add block trials to array
        experiment_trials.push(block_trials);
        // Clean block trials
        block_trials = new Array();
        current_block++;
        if (current_block + 1 > blocks.length)
            current_state = possible_states.EndExperiment;
        else 
            current_state = possible_states.StartBlock;
        break;
    case possible_states.StartRest:
        $("#experiment-info").hide();
        current_state = possible_states.DoingRest;
        doRest();
        break;
    case possible_states.EndExperiment:
        $("#experiment-info").hide();
        
        $("#send-data-btn").show();
        $("#send-data-btn").click(sendData);
        current_state = possible_states.WaitSendData;
        console.log('Experiment ended');
    default:
        //   console.log('Holaa')
        break;
  }
}



