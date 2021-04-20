<template>
  <div class="container">
    <h1 class="text-center">Experiment {{ exp_code }}</h1>
    <h2>Video instructions</h2>
    <div class="d-flex justify-content-center">
      <video-player
        class="vjs-custom-skin"
        ref="videoPlayer"
        :options="playerOptions"
        :playsinline="true"
        @play="onPlayerPlay($event)"
        @pause="onPlayerPause($event)"
        @ended="onPlayerEnded($event)"
        @loadeddata="onPlayerLoadeddata($event)"
        @waiting="onPlayerWaiting($event)"
        @playing="onPlayerPlaying($event)"
        @timeupdate="onPlayerTimeupdate($event)"
        @canplay="onPlayerCanplay($event)"
        @canplaythrough="onPlayerCanplaythrough($event)"
        @ready="playerReadied"
        @statechanged="playerStateChanged($event)"
      >
      </video-player>
    </div>
    <br />
    <h2>Consent</h2>
    <div class="d-flex justify-content-center">
      <embed
        src="http://127.0.0.1:8887/B2ZC/consent.pdf"
        width="640"
        height="480"
      />
    </div>
    <br />
    <a
      role="button"
      class="btn btn-primary btn-lg btn-block active text-center"
      :href="'/experiment/?code=' + exp_code"
      >Agree and continue to experiment</a
    >
    <br />
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      // videojs options
      playerOptions: {
        height: "640",
        autoplay: false,
        muted: true,
        language: "en",
        playbackRates: [1.0],
        sources: [
          {
            type: "video/mp4",
            // mp4
            src: "http://127.0.0.1:8887/B2ZC/out.mp4",
            // webm
            // src: "https://cdn.theguardian.tv/webM/2015/07/20/150716YesMen_synd_768k_vp8.webm"
          },
        ],
      },
    };
  },
  props: {
    exp_code: String,
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
    // listen event
    onPlayerPlay(player) {
      // console.log('player play!', player)
    },
    onPlayerPause(player) {
      // console.log('player pause!', player)
    },
    onPlayerEnded(player) {
      // console.log('player ended!', player)
    },
    onPlayerLoadeddata(player) {
      // console.log('player Loadeddata!', player)
    },
    onPlayerWaiting(player) {
      // console.log('player Waiting!', player)
    },
    onPlayerPlaying(player) {
      // console.log('player Playing!', player)
    },
    onPlayerTimeupdate(player) {
      // console.log('player Timeupdate!', player.currentTime())
    },
    onPlayerCanplay(player) {
      // console.log('player Canplay!', player)
    },
    onPlayerCanplaythrough(player) {
      // console.log('player Canplaythrough!', player)
    },
    // or listen state event
    playerStateChanged(playerCurrentState) {
      // console.log('player current update state', playerCurrentState)
    },
    // player is ready
    playerReadied(player) {
      // seek to 10s
      console.log("example player 1 readied", player);
      player.currentTime(0);
      // console.log('example 01: the player is readied', player)
    },
  },
};
</script>

<style scoped></style>
