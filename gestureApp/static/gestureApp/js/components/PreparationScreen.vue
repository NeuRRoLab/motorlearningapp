<template>
  <div class="container">
    <template v-if="!requirements_fulfilled">
      <h2>Experiment requirements</h2>
      <b-card>
        <b-card-text style="white-space: pre-wrap">{{
          requirements
        }}</b-card-text>
      </b-card>
      <br />
      <button
        class="btn btn-primary btn-lg btn-block active text-center"
        @click="requirements_fulfilled = true"
      >
        I fulfill the requirements to participate
      </button>
    </template>
    <template v-else-if="!video_seen">
      <h2>Video instructions</h2>
      <div class="d-flex justify-content-center">
        <video-player
          class="vjs-custom-skin"
          ref="videoPlayer"
          :options="playerOptions"
          :playsinline="true"
          @ready="playerReadied"
        >
        </video-player>
      </div>
      <br />
      <button
        class="btn btn-primary btn-lg btn-block active text-center"
        @click="video_seen = true"
      >
        Continue
      </button>
    </template>
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
      // videojs options
      playerOptions: {
        height: "480",
        autoplay: false,
        muted: true,
        language: "en",
        playbackRates: [1.0],
        sources: [
          {
            type: "video/mp4",
            // mp4
            src: this.video_url,
            // webm
            // src: "https://cdn.theguardian.tv/webM/2015/07/20/150716YesMen_synd_768k_vp8.webm"
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
    // player is ready
    playerReadied(player) {
      // seek to 10s
      console.log("example player 1 readied", player);
      player.muted(false);
      // player.currentTime(0);
      // console.log('example 01: the player is readied', player)
    },
  },
};
</script>

<style scoped></style>
