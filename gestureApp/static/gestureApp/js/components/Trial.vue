<!-- Component that manages the actual showing of keys in a screen and also captures the keypresses -->
<template>
  <div>
    <!-- If not resting -->
    <template v-if="!resting">
      <h4 class="text-center">Enter Key Sequence:</h4>
      <div class="text-center">
        <!-- For each character in the sequence, show the appropriate square for it -->
        <!-- If practicing, show the practice sequence -->
        <div
          :ref="'seq-' + (index - 1)"
          :value="practice ? practice_sequence : sequence[index - 1]"
          v-for="index in practice ? practice_sequence.length : sequence.length"
          class="seq-charact"
          :key="index - 1"
        >
          {{ practice ? practice_sequence[index - 1] : sequence[index - 1] }}
        </div>
      </div>
      <!-- Countdown timer -->
      <p class="text-center">
        Time left:
        <countdown
          ref="timerTrial"
          :time="max_time_per_trial * 1000"
          :interval="100"
          :auto-start="true"
          @end="trialEnded"
        >
          <span class="h2" slot-scope="props"
            >{{ props.seconds }}.{{
              Math.floor(props.milliseconds / 100)
            }}</span
          >
        </countdown>
        seconds
      </p>
    </template>
    <!-- Resting -->
    <template v-else>
      <h1 class="text-center">Rest</h1>
      <!-- Countdown timer -->
      <p class="text-center">
        Time left:
        <countdown
          ref="timerRest"
          :time="resting_time * 1000"
          :interval="100"
          :auto-start="false"
          :emit-events="true"
          @end="restEnded"
        >
          <span class="h2" slot-scope="props"
            >{{ props.seconds }}.{{
              Math.floor(props.milliseconds / 100)
            }}</span
          >
        </countdown>
        seconds
      </p>
    </template>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      current_inputted_sequence: [],
      keypresses_trial: [],
      resting: false,
      practice_sequence: "",
    };
  },
  props: {
    sequence: String,
    max_time_per_trial: Number,
    resting_time: Number,
    practice: Boolean,
    capturing_keypresses: Boolean,
    random_seq: Boolean,
    with_feedback: Boolean,
  },
  mounted: function () {
    // Add listener to keypresses
    window.addEventListener("keydown", this.keydownHandler);
    // Create random sequence for practice if needed
    if (this.practice && this.random_seq)
      this.practice_sequence = this.make_sequence(5);
    else if (this.practice && !this.random_seq)
      this.practice_sequence = this.sequence;
  },
  components: {},
  computed: {},
  watch: {},
  methods: {
    make_sequence(length) {
      // Make a random sequence of length 'length' using only characters from 1 to 5.
      var result = "";
      var characters = "12345";
      var charactersLength = characters.length;
      for (var i = 0; i < length; i++) {
        result += characters.charAt(
          Math.floor(Math.random() * charactersLength)
        );
      }
      return result;
    },
    stopPractice() {
      this.trialEnded(false);
    },
    trialEnded(do_rest = true, from_timer = false, started_trial_at = true) {
      // If the trial doesn't have a starting timestamp, then do nothing
      if (!started_trial_at) return;

      // Sequence the user is trying to complete
      let sequence = this.sequence;
      if (this.practice) sequence = this.practice_sequence;
      // Whether the inputted sequence matches the expected sequence
      let correct = this.current_inputted_sequence.join("") === sequence;
      // Whether the sequence was partially correct or not (user didn't manage to complete it, but started properly)
      let partial_correct = correct;
      if (from_timer && this.current_inputted_sequence.length > 0) {
        partial_correct =
          this.current_inputted_sequence.join("") ===
          sequence.slice(0, this.current_inputted_sequence.length);
      }

      // Avoid doing rest after finishing practice trials
      this.resting = true;
      if (do_rest) {
        // Submit trial to parent script
        this.$emit(
          "trial-ended",
          correct,
          this.keypresses_trial,
          this.current_inputted_sequence,
          sequence,
          partial_correct
        );
        // Start the resting countdown timer
        this.$nextTick(() => {
          if (this.$refs.timerRest) this.$refs.timerRest.start();
        });
      }
      // Create empty keypresses and inputted sequence arrays for a new trial
      this.keypresses_trial = new Array();
      this.current_inputted_sequence = new Array();
    },
    restEnded() {
      // Runs when rest ends
      this.$emit("rest-ended");
      this.resting = false;
      // Creates a new random practice sequence if practicing
      if (this.practice && this.random_seq)
        this.practice_sequence = this.makeid(5);
      else if (this.practice && !this.random_seq)
        this.practice_sequence = this.sequence;
    },
    keydownHandler: function (e) {
      // Manages input of keypresses
      // Do not count special keys
      if (
        e.key === "Alt" ||
        e.key === "Control" ||
        e.key === "Fn" ||
        e.key === "Shift" ||
        e.key === "s"
      )
        return;
      if (!this.resting && this.capturing_keypresses) {
        let sequence = this.sequence;
        if (this.practice) {
          sequence = this.practice_sequence;
        }
        // Get keypress timestamp.
        // TODO: could improve timing here
        var timestamp = new Date().getTime();
        this.current_inputted_sequence.push(e.key);
        // TODO: Only count digits as keypresses
        this.keypresses_trial.push({ value: e.key, timestamp: timestamp });
        // Check if the inputted key is correct
        var index = this.current_inputted_sequence.length - 1;
        // Color the key as correct both if it was correct, or if feedback is disabled
        if (sequence[index] === e.key || !this.with_feedback) {
          this.$refs["seq-" + index.toString()][0].style.backgroundColor =
            "#85C0F9";
        } else {
          this.$refs["seq-" + index.toString()][0].style.backgroundColor =
            "#F5793A";
        }
        // Finished sequence!
        if (
          this.current_inputted_sequence.join("") === sequence ||
          this.current_inputted_sequence.length >= sequence.length
        )
          this.$refs.timerTrial.end();
      }
    },
  },
  destroyed() {
    // Remove listener once the trials are done
    window.removeEventListener("keydown", this.keydownHandler);
  },
};
</script>

<style scoped></style>
