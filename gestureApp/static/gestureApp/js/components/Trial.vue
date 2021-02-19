<template>
  <div>
    <template v-if="!resting">
      <h4 class="text-center">Enter Key Sequence:</h4>
      <div class="text-center">
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
      <p class="text-center">
        Time left:
        <countdown
          ref="timerTrial"
          :time="max_time_per_trial * 1000"
          :interval="100"
          :auto-start="true"
          @end="trialEnded"
        >
          <template slot-scope="props"
            >{{ props.seconds }}.{{
              props.milliseconds / 100
            }}
            seconds.</template
          >
        </countdown>
      </p>
    </template>
    <template v-else>
      <h1 class="text-center">Rest</h1>
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
          <span slot-scope="props"
            >{{ props.seconds }}.{{ props.milliseconds / 100 }} seconds.</span
          >
        </countdown>
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
  },
  mounted: function () {
    window.addEventListener("keydown", this.keydownHandler);
    if (this.practice && this.random_seq)
      this.practice_sequence = this.makeid(5);
    else if (this.practice && !this.random_seq)
      this.practice_sequence = this.sequence;
  },
  components: {},
  computed: {},
  watch: {},
  methods: {
    makeid(length) {
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
    trialEnded(do_rest = true) {
      let sequence = this.sequence;
      if (this.practice) sequence = this.practice_sequence;
      let correct = this.current_inputted_sequence.join("") === sequence;

      this.resting = true;
      if (do_rest) {
        this.$emit(
          "trial-ended",
          correct,
          this.keypresses_trial,
          this.current_inputted_sequence,
          sequence
        );
        this.$nextTick(() => {
          if (this.$refs.timerRest) this.$refs.timerRest.start();
        });
      }
      this.keypresses_trial = new Array();
      this.current_inputted_sequence = new Array();
    },
    restEnded() {
      this.$emit("rest-ended");
      this.resting = false;
      if (this.practice && this.random_seq)
        this.practice_sequence = this.makeid(5);
      else if (this.practice && !this.random_seq)
        this.practice_sequence = this.sequence;
    },
    incorrectSequence() {
      this.$refs.timerTrial.end();
    },
    keydownHandler: function (e) {
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
        // TODO: Only count digits as keypresses
        let sequence = this.sequence;
        if (this.practice) {
          sequence = this.practice_sequence;
        }

        var timestamp = new Date().getTime();
        this.current_inputted_sequence.push(e.key);
        this.keypresses_trial.push({ value: e.key, timestamp: timestamp });
        // Check if the inputted key is correct
        var index = this.current_inputted_sequence.length - 1;
        if (sequence[index] === e.key) {
          this.$refs["seq-" + index.toString()][0].style.backgroundColor =
            "green";
        } else {
          this.$refs["seq-" + index.toString()][0].style.backgroundColor =
            "red";
          // this.incorrectSequence();
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
    window.removeEventListener("keydown", this.keydownHandler);
  },
};
</script>

<style scoped></style>
