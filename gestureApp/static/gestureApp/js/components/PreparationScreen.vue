<template>
  <div class="container">
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
    <h2>Consent</h2>
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
    <br />
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
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
  },
  mounted: function () {
    setTimeout(() => {
      console.log("dynamic change options", this.player);
      this.player.muted(false);
    }, 2000);
  },
  components: {},
  computed: {
    player() {
      return this.$refs.videoPlayer.player;
    },
  },
  watch: {},
  methods: {
    isObjectEmpty: function (obj) {
      return Object.keys(obj).length === 0 && obj.constructor === Object;
    },
    // player is ready
    playerReadied(player) {
      // seek to 10s
      console.log("example player 1 readied", player);
      // player.currentTime(0);
      // console.log('example 01: the player is readied', player)
    },
  },
};
</script>

<style scoped></style>
