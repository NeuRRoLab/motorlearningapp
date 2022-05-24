<!-- Shows the preparation screen before the experiment: requirements, consent form and instructions video -->
<template>
  <div class="container">
    <!-- First, show requirements -->
    <template v-if="!requirements_fulfilled">
      <h2>Experiment requirements</h2>
      <b-card>
        <b-card-text v-if="requirements !== ''" style="white-space: pre-wrap">{{
          requirements
        }}</b-card-text>
        <b-card-text v-else style="white-space: pre-wrap"
          >No experiment requirements</b-card-text
        >
      </b-card>
      <br />
      <button
        class="btn btn-primary btn-lg btn-block active text-center"
        @click="requirements_fulfilled = true"
      >
        I fulfill the requirements to participate
      </button>
    </template>
    <!-- Then, show video -->
    <template v-else-if="!video_seen">
      <h2>Video instructions</h2>
      <div class="d-flex justify-content-center">
        <video-player
          class="vjs-custom-skin"
          ref="videoPlayer"
          :options="playerOptions"
          :playsinline="true"
          @ended="playerEnded"
        >
        </video-player>
      </div>
      <br />
      <button
        id="continue-button"
        class="btn btn-primary btn-lg btn-block active text-center"
        :disabled="!video_ended"
        @click="video_seen = true"
      >
        Continue
      </button>
      <p class="text-center" v-if="!video_ended">
        To continue, you must finish watching the video.
      </p>
    </template>
    <!-- Finally, show consent form -->
    <template v-else>
      <h2>Consent Form</h2>
      <div class="d-flex justify-content-center">
        <embed :src="pdf_url" width="100%" height="480" />
      </div>
      <br />
      <button
        class="btn btn-primary btn-lg btn-block active text-center"
        @click="$emit('prep-screen-ready')"
      >
        Agree and continue to experiment
      </button>
    </template>
    <br />
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      requirements_fulfilled: false,
      video_seen: false,
      video_ended: false,
      // videojs options
      playerOptions: {
        width: "1080",
        autoplay: true,
        muted: false,
        language: "en",
        playbackRates: [1.0],
        sources: [
          {
            type: "video/mp4",
            src: this.video_url,
          },
        ],
      },
    };
  },
  props: {
    exp_code: String,
    video_url: String,
    pdf_url: String,
    requirements: String,
  },
  mounted: function () {},
  components: {},
  computed: {},
  watch: {},
  methods: {
    isObjectEmpty: function (obj) {
      return Object.keys(obj).length === 0 && obj.constructor === Object;
    },
    playerEnded(player) {
      this.video_ended = true;
    },
  },
};
</script>

<style scoped></style>
