"""
Master Orchestration Pipeline: Zack D. Films 3D Explainer & Instagram Auto-Publisher
Connects Topic -> Script -> Neural Voice -> 3D WebGL Scene -> Render & Mux -> Instagram Reels
"""

import re
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.config import REELS_DIR, DRAFTS_DIR
from core.script_engine import ScriptEngine
from core.voice_engine import VoiceEngine
from core.scene_builder import SceneBuilder
from core.renderer import Renderer
from core.instagram import InstagramPublisher


class Pipeline:
    def __init__(self):
        self.script_engine = ScriptEngine()
        self.voice_engine = VoiceEngine()
        self.scene_builder = SceneBuilder()
        self.renderer = Renderer()
        self.instagram = InstagramPublisher()

    def run(
        self,
        topic: str,
        publish: bool = False,
        draft: bool = False,
        custom_script: Optional[List[str]] = None,
        credentials: Optional[Dict[str, str]] = None,
        share_story: bool = True
    ) -> Dict[str, Any]:
        """
        Executes the end-to-end autonomous video creation and publishing workflow.
        """
        topic = topic.strip()
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', topic.lower()).strip('_')[:35]
        project_dir = REELS_DIR / f"zach_{slug}"
        project_dir.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 70)
        print(f"🎬 [1/5] GENERATING VIRAL 8-SENTENCE SCRIPT")
        print(f"    Topic: '{topic}'")
        print("=" * 70)

        script = custom_script or self.script_engine.generate(topic)
        for i, sentence in enumerate(script):
            print(f"  [{i+1}] {sentence}")

        script_file = project_dir / "script.json"
        script_file.write_text(json.dumps(script, indent=2), encoding="utf-8")

        print("\n" + "=" * 70)
        print("🎙️ [2/5] NEURAL VOICE SYNTHESIS & WORD TIMESTAMPS")
        print("=" * 70)

        voice_res = self.voice_engine.synthesize(script, project_dir)
        total_duration = voice_res["duration"]
        captions = voice_res["captions"]
        meta_lines = voice_res.get("meta_lines")
        vo_wav = voice_res["vo_wav"]

        print(f"[+] Voice duration: {total_duration:.2f}s ({len(captions)} caption blocks)")

        print("\n" + "=" * 70)
        print("📐 [3/5] BUILDING 3D PROCEDURAL SCENE (Three.js WebGL)")
        print("=" * 70)

        self.scene_builder.setup_project(project_dir)
        shots_file = self.scene_builder.build_shots_file(project_dir, captions, total_duration, meta_lines, topic=topic)
        print(f"[+] Scene environment ready with zoomed-out 9:16 camera framing")

        print("\n" + "=" * 70)
        print("🎥 [4/5] RENDERING WEBGL & BROADCAST EBU R128 MUXING")
        print("=" * 70)

        silent_mp4 = self.renderer.render_webgl(project_dir, fps=30)
        final_mp4 = project_dir / f"zach_{slug}_final.mp4"
        out_video = self.renderer.mux_audio_video(silent_mp4, vo_wav, final_mp4)

        cover_jpg = project_dir / "cover.jpg"
        self.renderer.extract_cover(out_video, cover_jpg, timestamp=1.2)
        self.renderer.clean_intermediates(project_dir)

        file_size_mb = out_video.stat().st_size / (1024 * 1024)
        print(f"[+] Render complete: {out_video.name} ({file_size_mb:.2f} MB, {total_duration:.2f}s)")

        # Result dictionary
        result: Dict[str, Any] = {
            "topic": topic,
            "duration": total_duration,
            "video_path": str(out_video),
            "cover_path": str(cover_jpg),
            "file_size_mb": round(file_size_mb, 2),
            "script": script,
            "published": False,
            "draft": False,
        }

        # Save to draft if requested
        if draft:
            print("\n" + "=" * 70)
            print("💾 SAVING TO DRAFTS")
            print("=" * 70)
            draft_dir = DRAFTS_DIR / f"draft_{slug}"
            draft_dir.mkdir(parents=True, exist_ok=True)
            draft_video = draft_dir / f"{slug}.mp4"
            draft_cover = draft_dir / "cover.jpg"
            shutil.copy2(str(out_video), str(draft_video))
            if cover_jpg.exists():
                shutil.copy2(str(cover_jpg), str(draft_cover))

            meta = {
                "topic": topic,
                "duration": total_duration,
                "created_at": str(Path(out_video).stat().st_ctime),
                "script": script,
                "video_path": str(draft_video),
                "cover_path": str(draft_cover),
            }
            (draft_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
            result["draft"] = True
            result["draft_path"] = str(draft_dir)
            print(f"[+] Draft stored at: {draft_dir}")

        # Publish to Instagram if requested
        if publish:
            print("\n" + "=" * 70)
            print("🚀 [5/5] PUBLISHING TO INSTAGRAM REELS")
            print("=" * 70)

            # Handle credentials if provided
            if credentials:
                if credentials.get("session_id"):
                    self.instagram.login_with_credentials("", session_id=credentials["session_id"])
                elif credentials.get("username") and credentials.get("password"):
                    self.instagram.login_with_credentials(
                        credentials["username"],
                        credentials["password"],
                        verification_code=credentials.get("2fa")
                    )

            # Check if authenticated or prompt
            if not self.instagram.is_authenticated():
                print("[!] Instagram authentication required.")
                if not self.instagram.login_interactive():
                    print("[-] Skipping Instagram upload due to missing authentication.")
                    return result

            # Get logged-in user handle for personalized caption CTA
            account_handle = ""
            try:
                prof = self.instagram.get_profile()
                account_handle = prof.get("username", "")
            except Exception:
                cl = self.instagram.get_client()
                if cl and hasattr(cl, "username"):
                    account_handle = cl.username

            follow_cta = f"Follow @{account_handle}" if account_handle else "Follow"

            # Craft viral Instagram caption & hashtags
            caption = (
                f"Wait... is this REALLY how {topic.rstrip('?.!')} works? 🤯\n\n"
                f"Here is what actually happens behind the scenes:\n"
                f"• {script[2]}\n"
                f"• {script[3]}\n"
                f"• {script[4]}\n"
                f"• {script[6]}\n\n"
                f"Did you know this before? Drop your thoughts below! 👇\n\n"
                f"{follow_cta} for daily 3D explainers, hidden technology & viral science! 🚀\n"
                f".\n.\n"
                f"#tech #science #3danimation #zackdfilms #howitworks #technology #animation #viral #reels #explainer #interestingfacts"
            )
            comment = f"Drop a ❤️ and save this! Did you think it worked like this before? Tell us below! 👇"

            upload_res = self.instagram.upload_reel(
                video_path=str(out_video),
                caption=caption,
                cover_path=str(cover_jpg) if cover_jpg.exists() else None
            )

            media_id = upload_res.get("media_id")
            reel_url = upload_res.get("url")
            result["published"] = True
            result["media_id"] = media_id
            result["reel_url"] = reel_url

            if media_id:
                boost_msg = "like, pinned CTA" + (", story reshare" if share_story else "")
                print(f"\n[+] Boosting Reel with automated engagement ({boost_msg})...")
                boost_res = self.instagram.boost_engagement(
                    media_id=media_id,
                    comment_text=comment,
                    like=True,
                    share_story=share_story,
                    video_path=str(out_video)
                )
                result["boost"] = boost_res

        return result


pipeline = Pipeline()

